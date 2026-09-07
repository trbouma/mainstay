from __future__ import annotations

import json
import re
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
    base_url = safebox.require_url("local", purpose="web").rstrip("/")
    target = (
        f"{base_url}/.well-known/nostr.json?{urlencode({'name': normalized_handle})}"
    )
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
            body = response.read(MAX_DIRECTORY_BYTES + 1)
    except HTTPError as exc:
        if exc.code == 404:
            raise LocalClearError(
                f"handle {normalized_handle!r} is not registered in this Mainstay"
            ) from exc
        raise LocalClearError(
            f"local Safebox directory returned HTTP {exc.code}"
        ) from exc
    except URLError as exc:
        raise LocalClearError(
            f"local Safebox directory is unavailable: {exc.reason}"
        ) from exc
    except TimeoutError as exc:
        raise LocalClearError("local Safebox directory timed out") from exc

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
            recipient.pubkey,
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
    return _redacted_receipt(result, recipient)


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
