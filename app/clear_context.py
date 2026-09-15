from __future__ import annotations

import json
import os
import re
import sqlite3
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .registry import BundleConfig

MAX_DIRECTORY_BYTES = 64 * 1024
LOCAL_HANDLE_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?$")


class LocalClearError(RuntimeError):
    pass


@dataclass(frozen=True)
class LocalClearRecipient:
    handle: str
    pubkey: str


@dataclass(frozen=True)
class RegisteredHandle:
    handle: str
    pubkey: str
    npub: str
    relays: tuple[str, ...]


def list_registered_handles(
    *,
    database_path: Path,
) -> list[RegisteredHandle]:
    if not database_path.exists():
        raise LocalClearError(f"Safebox database is unavailable: {database_path}")
    try:
        with sqlite3.connect(
            f"file:{database_path}?mode=ro",
            uri=True,
        ) as connection:
            rows = connection.execute(
                """
                SELECT claimed_handle, npub, home_relay
                FROM claimed_handle
                ORDER BY claimed_handle
                """
            ).fetchall()
    except sqlite3.Error as exc:
        raise LocalClearError(f"could not read Safebox handle database: {exc}") from exc

    registered: list[RegisteredHandle] = []
    for raw_handle, raw_npub, raw_home_relay in rows:
        handle = str(raw_handle).strip().lower()
        if not LOCAL_HANDLE_PATTERN.fullmatch(handle):
            continue
        npub = str(raw_npub or "").strip()
        pubkey = _pubkey_from_npub(npub)
        if not pubkey:
            continue
        home_relay = str(raw_home_relay or "").strip()
        relays = (home_relay,) if home_relay else ()
        registered.append(
            RegisteredHandle(
                handle=handle,
                pubkey=pubkey,
                npub=npub,
                relays=relays,
            )
        )
    return registered


def resolve_local_clear_recipient(
    bundle: BundleConfig,
    handle: str,
    *,
    timeout: float,
) -> LocalClearRecipient:
    normalized_handle = str(handle).strip().lower()
    if "@" in normalized_handle or not LOCAL_HANDLE_PATTERN.fullmatch(
        normalized_handle
    ):
        raise LocalClearError(
            "recipient must be a bare handle registered in this Mainstay instance"
        )

    safebox = bundle.require_service("safebox_web")
    if not safebox.enabled:
        raise LocalClearError("the Mainstay Safebox service is disabled")
    body = _read_safebox_directory(safebox, normalized_handle, timeout=timeout)

    if len(body) > MAX_DIRECTORY_BYTES:
        raise LocalClearError("local Safebox directory response is too large")
    try:
        payload = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LocalClearError("local Safebox directory returned invalid JSON") from exc
    if not isinstance(payload, dict):
        raise LocalClearError("local Safebox directory returned an invalid response")

    names = payload.get("names")
    pubkey = names.get(normalized_handle) if isinstance(names, dict) else None
    if not isinstance(pubkey, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", pubkey):
        raise LocalClearError(
            f"handle {normalized_handle!r} is not registered in this Mainstay"
        )

    clear = payload.get("clear")
    descriptor = clear.get(normalized_handle) if isinstance(clear, dict) else None
    if not _supports_clear_transfer(descriptor):
        raise LocalClearError(
            f"local handle {normalized_handle!r} does not advertise Clear support"
        )
    return LocalClearRecipient(normalized_handle, pubkey.lower())


def _read_safebox_directory(
    safebox,
    handle: str | None,
    *,
    timeout: float,
) -> bytes:
    errors: list[str] = []
    seen: set[str] = set()
    for scope in ("local", "internal"):
        try:
            base_url = safebox.require_url(scope, purpose="web").rstrip("/")
        except ValueError:
            continue
        if base_url in seen:
            continue
        seen.add(base_url)
        target = f"{base_url}/.well-known/nostr.json"
        if handle is not None:
            target = f"{target}?{urlencode({'name': handle})}"
        request = Request(
            target,
            headers={
                "Accept": "application/json",
                "User-Agent": "mainstay-local",
            },
        )
        try:
            with urlopen(request, timeout=timeout) as response:
                if not 200 <= response.status < 300:
                    raise LocalClearError(
                        f"local Safebox directory returned HTTP {response.status}"
                    )
                return response.read(MAX_DIRECTORY_BYTES + 1)
        except HTTPError as exc:
            if exc.code == 404 and handle is not None:
                raise LocalClearError(
                    f"handle {handle!r} is not registered in this Mainstay"
                ) from exc
            raise LocalClearError(
                f"local Safebox directory returned HTTP {exc.code}"
            ) from exc
        except URLError as exc:
            errors.append(f"{base_url}: {exc.reason}")
        except TimeoutError:
            errors.append(f"{base_url}: timed out")
    detail = "; ".join(errors) if errors else "no Safebox web endpoint configured"
    raise LocalClearError(f"local Safebox directory is unavailable: {detail}")


def _npub_from_pubkey(pubkey: str) -> str:
    try:
        from stroma import Keys

        return Keys(pub_k=pubkey).public_key_bech32()
    except Exception:
        return ""


def _pubkey_from_npub(npub: str) -> str:
    try:
        from stroma import Keys

        return Keys(pub_k=npub).public_key_hex()
    except Exception:
        return ""


def _supports_clear_transfer(descriptor: Any) -> bool:
    if not isinstance(descriptor, dict):
        return False
    protocols = descriptor.get("protocols")
    transports = descriptor.get("transports")
    raw_kinds = descriptor.get("kinds")
    if not all(isinstance(value, list) for value in (protocols, transports, raw_kinds)):
        return False
    try:
        kinds = {int(value) for value in raw_kinds}
    except (TypeError, ValueError):
        return False
    return (
        "clear-token-transfer" in protocols and "nip59" in transports and 7379 in kinds
    )


def send_local_clear(
    bundle: BundleConfig,
    *,
    amount: int,
    handle: str,
    memo: str | None,
    compose_path: Path,
    env_path: Path | None,
    timeout: float,
) -> dict[str, Any]:
    if amount <= 0:
        raise LocalClearError("amount must be greater than zero")
    if timeout <= 0:
        raise LocalClearError("timeout must be greater than zero")
    if memo is not None and len(memo) > 200:
        raise LocalClearError("memo must be 200 characters or fewer")

    recipient = resolve_local_clear_recipient(bundle, handle, timeout=timeout)
    clear = bundle.require_service("clear")
    spurline = bundle.require_service("spurline")
    if not clear.enabled or not spurline.enabled:
        raise LocalClearError("internal Clear and Spurline services must be enabled")
    clear.require_url("internal", purpose="mint")
    relay = spurline.require_url("internal", purpose="relay")

    operator_token = os.getenv("CLEAR_OPERATOR_TOKEN")
    if operator_token:
        operator_url = os.getenv("CLEAR_OPERATOR_API_URL") or clear.require_url(
            "internal", purpose="mint"
        )
        try:
            result = _send_via_clear_operator_api(
                operator_url,
                operator_token=operator_token,
                amount=amount,
                recipient_pubkey=recipient.pubkey,
                memo=memo,
                relay=relay,
                timeout=timeout,
            )
            return _redacted_receipt(result, recipient)
        except LocalClearError as exc:
            if "404" not in str(exc):
                raise

    result = _send_via_docker_compose(
        amount=amount,
        recipient_pubkey=recipient.pubkey,
        memo=memo,
        compose_path=compose_path,
        env_path=env_path,
        relay=relay,
    )
    return _redacted_receipt(result, recipient)


def _send_via_clear_operator_api(
    clear_url: str,
    *,
    operator_token: str,
    amount: int,
    recipient_pubkey: str,
    memo: str | None,
    relay: str,
    timeout: float,
) -> dict[str, Any]:
    request = Request(
        f"{clear_url.rstrip('/')}/v1/operator/root/send",
        data=json.dumps(
            {
                "amount": amount,
                "address": recipient_pubkey,
                "memo": memo,
                "relays": [relay],
                "allow_internal_mint_delivery": True,
            }
        ).encode(),
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {operator_token}",
            "Content-Type": "application/json",
            "User-Agent": "mainstay-local",
        },
        method="POST",
    )
    try:
        with urlopen(request, timeout=max(10, timeout)) as response:
            body = response.read()
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise LocalClearError(
            f"Clear root send API returned HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise LocalClearError(
            f"Clear root send API is unavailable: {exc.reason}"
        ) from exc
    try:
        result = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LocalClearError(
            "Clear root send API reported success but returned unreadable JSON; "
            "do not retry without reconciling the root wallet"
        ) from exc
    if not isinstance(result, dict):
        raise LocalClearError(
            "Clear root send API reported success without a structured receipt; "
            "do not retry without reconciling the root wallet"
        )
    return result


def _send_via_docker_compose(
    *,
    amount: int,
    recipient_pubkey: str,
    memo: str | None,
    compose_path: Path,
    env_path: Path | None,
    relay: str,
) -> dict[str, Any]:
    command = ["docker", "compose"]
    if env_path is not None:
        command.extend(["--env-file", str(env_path)])
    command.extend(
        [
            "-f",
            str(compose_path),
            "exec",
            "-T",
            "clear",
            "clear-root",
            "send",
            str(amount),
            recipient_pubkey,
            "--allow-internal-mint-delivery",
            "--relay",
            relay,
        ]
    )
    if memo:
        command.extend(["--memo", memo])

    try:
        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise LocalClearError(f"could not run Docker Compose: {exc}") from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or "clear-root delivery failed"
        raise LocalClearError(detail)

    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise LocalClearError(
            "clear-root reported success but returned an unreadable receipt; "
            "do not retry without reconciling the root wallet"
        ) from exc
    if not isinstance(result, dict):
        raise LocalClearError(
            "clear-root reported success without a structured receipt; "
            "do not retry without reconciling the root wallet"
        )
    return result


def _redacted_receipt(
    result: dict[str, Any],
    recipient: LocalClearRecipient,
) -> dict[str, Any]:
    delivery = result.get("delivery")
    publish = result.get("publish")
    delivery = delivery if isinstance(delivery, dict) else {}
    publish = publish if isinstance(publish, dict) else {}
    return {
        "status": str(publish.get("status") or "OK"),
        "amount": int(result.get("amount") or 0),
        "unit": str(result.get("unit") or ""),
        "mint": str(result.get("mint") or ""),
        "recipient": {
            "handle": recipient.handle,
            "npub": str(delivery.get("recipient_npub") or ""),
        },
        "delivery": {
            "event_id": str(publish.get("event_id") or ""),
            "relays": list(publish.get("relays") or []),
            "verified_relays": list(publish.get("verified_relays") or []),
            "verified": bool(publish.get("verified")),
        },
    }
