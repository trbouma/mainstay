from __future__ import annotations

import json
import os
import re
import secrets
import sqlite3
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from stroma import Event, Keys
from stroma import KeyError as StromaKeyError

from .registry import BundleConfig

MAX_DIRECTORY_BYTES = 64 * 1024
LOCAL_HANDLE_PATTERN = re.compile(r"^[a-z0-9](?:[a-z0-9._-]{0,62}[a-z0-9])?$")
TREASURY_EVENT_KIND = 37379


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


def clear_info(
    bundle: BundleConfig,
    *,
    timeout: float,
) -> dict[str, Any]:
    if timeout <= 0:
        raise LocalClearError("timeout must be greater than zero")
    clear = bundle.require_service("clear")
    if not clear.enabled:
        raise LocalClearError("the Mainstay Clear service is disabled")
    clear_url = clear.require_url("internal", purpose="mint")
    info = _clear_request_json(
        clear_url,
        "GET",
        "/v1/info",
        timeout=timeout,
    )
    result: dict[str, Any] = {
        "status": "OK",
        "mint": clear_url,
        "info": info,
    }
    operator_token = os.getenv("CLEAR_OPERATOR_TOKEN")
    if operator_token:
        operator_url = os.getenv("CLEAR_OPERATOR_API_URL") or clear_url
        try:
            summary = _clear_request_json(
                operator_url,
                "GET",
                "/v1/operator/summary",
                token=operator_token,
                timeout=timeout,
            )
            result["root_summary"] = summary
        except LocalClearError as exc:
            result["root_summary_error"] = str(exc)
    return result


def list_clear_cmus(
    bundle: BundleConfig,
    *,
    timeout: float,
) -> dict[str, Any]:
    if timeout <= 0:
        raise LocalClearError("timeout must be greater than zero")
    clear = bundle.require_service("clear")
    if not clear.enabled:
        raise LocalClearError("the Mainstay Clear service is disabled")
    operator_token = os.getenv("CLEAR_OPERATOR_TOKEN")
    if not operator_token:
        raise LocalClearError("CLEAR_OPERATOR_TOKEN must be set to list Clear CMUs")
    clear_url = clear.require_url("internal", purpose="mint")
    operator_url = os.getenv("CLEAR_OPERATOR_API_URL") or clear_url
    info = _clear_request_json(clear_url, "GET", "/v1/info", timeout=timeout)
    root_unit = _root_cmu_unit(info)
    cmus = _clear_request_json(
        operator_url,
        "GET",
        "/v1/operator/cmus",
        token=operator_token,
        timeout=timeout,
    )
    items = cmus.get("cmus") if isinstance(cmus, dict) else None
    if not isinstance(items, list):
        raise LocalClearError("Clear CMU list endpoint returned an invalid response")
    annotated = []
    for item in items:
        if not isinstance(item, dict):
            continue
        unit = str(item.get("unit") or "")
        annotated.append(
            {
                **item,
                "instance_owned": bool(root_unit and unit == root_unit),
            }
        )
    return {
        "status": "OK",
        "mint": clear_url,
        "instance_cmu": root_unit,
        "cmus": annotated,
    }


def bootstrap_clear_cmu(
    bundle: BundleConfig,
    *,
    name: str,
    unit_alias: str | None,
    timeout: float,
    lifetime_seconds: int = 300,
) -> dict[str, Any]:
    if timeout <= 0:
        raise LocalClearError("timeout must be greater than zero")
    if lifetime_seconds <= 0:
        raise LocalClearError("lifetime must be greater than zero")
    treasurer_nsec = os.getenv("MAINSTAY_TREASURER_NSEC", "").strip()
    if not treasurer_nsec:
        raise LocalClearError("MAINSTAY_TREASURER_NSEC must be set")
    try:
        treasurer_npub = Keys(priv_k=treasurer_nsec).public_key_bech32()
    except StromaKeyError as exc:
        raise LocalClearError("MAINSTAY_TREASURER_NSEC is invalid") from exc

    clear = bundle.require_service("clear")
    if not clear.enabled:
        raise LocalClearError("the Mainstay Clear service is disabled")
    operator_token = os.getenv("CLEAR_OPERATOR_TOKEN")
    if not operator_token:
        raise LocalClearError("CLEAR_OPERATOR_TOKEN must be set")

    clear_url = clear.require_url("internal", purpose="mint")
    operator_url = os.getenv("CLEAR_OPERATOR_API_URL") or clear_url
    info = _clear_request_json(clear_url, "GET", "/v1/info", timeout=timeout)
    mint_url = str(info.get("mint_url") or clear_url).rstrip("/")

    treasurer = _clear_request_json(
        operator_url,
        "POST",
        "/v1/operator/treasurers",
        payload={"npub": treasurer_npub},
        token=operator_token,
        timeout=timeout,
        label="Clear treasurer add API",
    )
    grant = _clear_request_json(
        operator_url,
        "POST",
        "/v1/operator/treasurer-grants",
        payload={"npub": treasurer_npub},
        token=operator_token,
        timeout=timeout,
        label="Clear treasurer grant API",
    )
    grant_id = grant.get("id")
    if not isinstance(grant_id, str) or not grant_id:
        raise LocalClearError("Clear treasurer grant API returned no grant id")

    cmu = _clear_request_json(
        clear_url,
        "POST",
        "/v1/treasury/cmus",
        payload=_build_cmu_create_envelope(
            mint=mint_url,
            grant_id=grant_id,
            name=name,
            unit_alias=unit_alias,
            nsec=treasurer_nsec,
            lifetime_seconds=lifetime_seconds,
        ),
        timeout=timeout,
        label="Clear treasury CMU create API",
    )
    return {
        "status": "OK",
        "mint": clear_url,
        "treasurer_npub": treasurer_npub,
        "treasurer": treasurer,
        "grant": grant,
        "cmu": cmu,
    }


def clear_root_wallet_balance(
    *,
    wallet_path: Path,
) -> dict[str, Any]:
    try:
        if wallet_path.exists():
            wallet = json.loads(wallet_path.read_text(encoding="utf-8"))
        else:
            wallet = {"version": 1, "entries": []}
    except (OSError, json.JSONDecodeError) as exc:
        raise LocalClearError(f"could not read Clear root wallet: {exc}") from exc
    if not isinstance(wallet, dict) or wallet.get("version") != 1:
        raise LocalClearError("Clear root wallet has an unsupported format")
    entries = wallet.get("entries")
    if not isinstance(entries, list):
        raise LocalClearError("Clear root wallet entries are unavailable")

    balances: dict[tuple[str, str], int] = {}
    safe_entry_count = 0
    for entry in entries:
        if not isinstance(entry, dict):
            continue
        mint = str(entry.get("mint") or "")
        unit = str(entry.get("unit") or "")
        proofs = entry.get("proofs")
        if not mint or not unit or not isinstance(proofs, list):
            continue
        safe_entry_count += 1
        total = 0
        for proof in proofs:
            if not isinstance(proof, dict):
                continue
            try:
                total += int(proof.get("amount") or 0)
            except (TypeError, ValueError):
                continue
        key = (mint, unit)
        balances[key] = balances.get(key, 0) + total
    return {
        "status": "OK",
        "wallet": str(wallet_path),
        "entries": safe_entry_count,
        "balances": [
            {"mint": mint, "unit": unit, "amount": amount}
            for (mint, unit), amount in sorted(balances.items())
        ],
    }


def _build_cmu_create_envelope(
    *,
    mint: str,
    grant_id: str,
    name: str,
    unit_alias: str | None,
    nsec: str,
    lifetime_seconds: int,
) -> dict[str, Any]:
    now = int(time.time())
    payload = {
        "action": "cmu:create",
        "grant_id": grant_id,
        "mint": mint.rstrip("/"),
        "name": name,
        "unit_alias": unit_alias,
        "nonce": secrets.token_hex(32),
        "created_at": now,
        "expires_at": now + lifetime_seconds,
    }
    return {"payload": payload, "event": _sign_treasury_payload(payload, nsec)}


def _sign_treasury_payload(payload: dict[str, Any], nsec: str) -> dict[str, Any]:
    try:
        event = Event(
            kind=TREASURY_EVENT_KIND,
            content=json.dumps(
                payload,
                sort_keys=True,
                separators=(",", ":"),
                ensure_ascii=False,
            ),
            tags=[],
            created_at=int(payload["created_at"]),
        )
        event.sign(Keys(priv_k=nsec))
    except StromaKeyError as exc:
        raise LocalClearError("treasurer key cannot sign CMU request") from exc
    return event.data()


def _root_cmu_unit(info: dict[str, Any]) -> str | None:
    currency = info.get("currency")
    if not isinstance(currency, dict):
        return None
    unit = currency.get("unit")
    return unit if isinstance(unit, str) and unit.startswith("cmu-") else None


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
    payload = {
        "amount": amount,
        "address": recipient_pubkey,
        "memo": memo,
        "relays": [relay],
        "allow_internal_mint_delivery": True,
    }
    return _clear_request_json(
        clear_url,
        "POST",
        "/v1/operator/root/send",
        payload=payload,
        token=operator_token,
        timeout=max(10, timeout),
        label="Clear root send API",
    )


def _clear_request_json(
    base_url: str,
    method: str,
    path: str,
    *,
    payload: dict[str, Any] | None = None,
    token: str | None = None,
    timeout: float,
    label: str = "Clear API",
) -> dict[str, Any]:
    headers = {
        "Accept": "application/json",
        "User-Agent": "mainstay-local",
    }
    data = None
    if payload is not None:
        data = json.dumps(payload).encode()
        headers["Content-Type"] = "application/json"
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(
        f"{base_url.rstrip('/')}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = response.read()
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise LocalClearError(f"{label} returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise LocalClearError(f"{label} is unavailable: {exc.reason}") from exc
    try:
        result = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise LocalClearError(f"{label} returned unreadable JSON") from exc
    if not isinstance(result, dict):
        raise LocalClearError(f"{label} returned an invalid response")
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
