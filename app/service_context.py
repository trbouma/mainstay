"""Context-aware commissioning for Mainstay-managed services."""

from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from typing import Any

from stroma import Event, Keys
from stroma import EventError as StromaEventError
from stroma import KeyError as StromaKeyError

APPLICATION_EVENT_KIND = 78
ADDRESSABLE_APPLICATION_EVENT_KIND = 30078
REQUEST_SCHEMA = "org.mainstay.service-commissioning-request"
ATTESTATION_SCHEMA = "org.mainstay.service-operator-attestation"
SERVICE_TYPES = {"clear": "clear-mint"}
MAX_CLOCK_SKEW_SECONDS = 5 * 60
DEFAULT_IDENTITY_STATE_PATH = Path(
    "build/mainstay-local/installation-identity.json"
)


class ServiceCommissioningError(RuntimeError):
    pass


def installation_keys(env_path: Path, state_path: Path) -> Keys:
    secret = _env_value(env_path, "MAINSTAY_INSTALLATION_NSEC")
    if not secret:
        raise ServiceCommissioningError(
            "MAINSTAY_INSTALLATION_NSEC is missing; run ./init-env.sh"
        )
    try:
        keys = Keys(priv_k=secret)
    except StromaKeyError as exc:
        raise ServiceCommissioningError(
            "MAINSTAY_INSTALLATION_NSEC is invalid"
        ) from exc
    expected = {
        "schema": "org.mainstay.installation-identity",
        "schema_version": 1,
        "npub": keys.public_key_bech32(),
    }
    if state_path.exists():
        try:
            recorded = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ServiceCommissioningError(
                f"installation identity sentinel is unreadable: {exc}"
            ) from exc
        if recorded != expected:
            raise ServiceCommissioningError(
                "configured Mainstay installation key does not match the "
                f"identity sentinel at {state_path}"
            )
        return keys

    state_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = state_path.with_suffix(state_path.suffix + ".tmp")
    try:
        temporary.write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
        temporary.chmod(0o600)
        temporary.replace(state_path)
    except OSError as exc:
        raise ServiceCommissioningError(
            f"could not record installation identity sentinel: {exc}"
        ) from exc
    return keys


def commission_service(
    service: str,
    *,
    compose_path: Path,
    env_path: Path,
    state_path: Path = DEFAULT_IDENTITY_STATE_PATH,
    relay: str,
    publish: bool = True,
) -> dict[str, Any]:
    service_type = _service_type(service)
    authority = installation_keys(env_path, state_path)
    request_result = _run_clear(
        ["service", "request", authority.public_key_bech32()],
        compose_path=compose_path,
        env_path=env_path,
    )
    request_data = request_result.get("commissioning_request")
    if not isinstance(request_data, dict):
        raise ServiceCommissioningError(
            "Clear returned no signed commissioning request"
        )
    request, request_content = _verify_request(
        request_data,
        authority=authority,
        service_type=service_type,
    )
    attestation = _create_attestation(
        request,
        request_content,
        authority=authority,
        service_type=service_type,
    )
    commissioned = _run_clear(
        ["service", "commission"],
        compose_path=compose_path,
        env_path=env_path,
        input_data=attestation,
        uncertain_on_parse=True,
    )
    identity = commissioned.get("service_identity")
    descriptor = commissioned.get("service_descriptor")
    if (
        not isinstance(identity, dict)
        or identity.get("state") != "commissioned"
        or not isinstance(descriptor, dict)
    ):
        raise ServiceCommissioningError(
            "Clear did not confirm a commissioned service identity; "
            "do not retry without checking `mainstay-local service show clear`"
        )
    try:
        reported_service_hex = Keys(
            pub_k=str(identity.get("npub") or "")
        ).public_key_hex()
    except StromaKeyError as exc:
        raise ServiceCommissioningError(
            "Clear reported an invalid commissioned service identity"
        ) from exc
    if reported_service_hex != request.pub_key:
        raise ServiceCommissioningError(
            "Clear commissioned a different service identity than it requested"
        )
    verification = _run_clear(
        ["service", "verify"],
        compose_path=compose_path,
        env_path=env_path,
        uncertain_on_parse=True,
    )
    expected_verification = {
        "state": "commissioned",
        "service_key_control": "verified",
        "operator_authorship": "verified",
        "reciprocal_relationship": "verified",
        "operator_npub": authority.public_key_bech32(),
        "commissioning_request_event_id": request.id,
        "operator_attestation_event_id": attestation["id"],
        "service_descriptor_event_id": descriptor.get("id"),
    }
    if any(
        verification.get(key) != value
        for key, value in expected_verification.items()
    ):
        raise ServiceCommissioningError(
            "Clear service verification did not match the commissioned evidence"
        )
    publication = None
    if publish:
        publication = _run_clear(
            ["service", "publish", "--relay", relay],
            compose_path=compose_path,
            env_path=env_path,
            uncertain_on_parse=True,
        )
    return {
        "state": "commissioned",
        "service": service,
        "service_npub": identity.get("npub"),
        "installation_npub": authority.public_key_bech32(),
        "commissioning_request_event_id": request.id,
        "operator_attestation_event_id": attestation["id"],
        "service_descriptor_event_id": descriptor.get("id"),
        "verification": verification,
        "publication": publication,
    }


def show_service(
    service: str,
    *,
    compose_path: Path,
    env_path: Path,
) -> dict[str, Any]:
    _service_type(service)
    return _run_clear(
        ["service", "show"],
        compose_path=compose_path,
        env_path=env_path,
    )


def verify_service(
    service: str,
    *,
    compose_path: Path,
    env_path: Path,
) -> dict[str, Any]:
    _service_type(service)
    return _run_clear(
        ["service", "verify"],
        compose_path=compose_path,
        env_path=env_path,
    )


def _service_type(service: str) -> str:
    normalized = service.strip().lower()
    if normalized not in SERVICE_TYPES:
        supported = ", ".join(sorted(SERVICE_TYPES))
        raise ServiceCommissioningError(
            f"unsupported managed service {service!r}; currently supported: {supported}"
        )
    return SERVICE_TYPES[normalized]


def _verify_request(
    event_data: dict[str, Any],
    *,
    authority: Keys,
    service_type: str,
) -> tuple[Event, dict[str, Any]]:
    try:
        event = Event.load(event_data, validate=True)
    except (StromaEventError, TypeError, ValueError) as exc:
        raise ServiceCommissioningError(
            "service commissioning request is not a valid Nostr event"
        ) from exc
    if event is None:
        raise ServiceCommissioningError(
            "service commissioning request signature is invalid"
        )
    try:
        content = json.loads(event.content)
    except json.JSONDecodeError as exc:
        raise ServiceCommissioningError(
            "service commissioning request content is invalid JSON"
        ) from exc
    if not isinstance(content, dict):
        raise ServiceCommissioningError(
            "service commissioning request content must be an object"
        )
    if event.kind != APPLICATION_EVENT_KIND:
        raise ServiceCommissioningError(
            "service commissioning request uses an unsupported event kind"
        )
    expected_service = {"pubkey": event.pub_key, "type": service_type}
    if content.get("schema") != REQUEST_SCHEMA or content.get("schema_version") != 1:
        raise ServiceCommissioningError(
            "service commissioning request uses an unsupported schema"
        )
    if content.get("service") != expected_service:
        raise ServiceCommissioningError(
            "service commissioning request identity or type does not match"
        )
    if content.get("management") != "mainstay-managed":
        raise ServiceCommissioningError(
            "service commissioning request is not Mainstay-managed"
        )
    if content.get("requested_operator") != authority.public_key_hex():
        raise ServiceCommissioningError(
            "service requested a different commissioning authority"
        )
    current = int(time.time())
    if event.created_at > current + MAX_CLOCK_SKEW_SECONDS:
        raise ServiceCommissioningError(
            "service commissioning request is dated too far in the future"
        )
    if content.get("issued_at") != event.created_at:
        raise ServiceCommissioningError(
            "service commissioning request issue time does not match"
        )
    expires_at = content.get("expires_at")
    if not isinstance(expires_at, int) or expires_at <= current:
        raise ServiceCommissioningError("service commissioning request has expired")
    if expires_at - event.created_at != 24 * 60 * 60:
        raise ServiceCommissioningError(
            "service commissioning request has an invalid validity period"
        )
    nonce = content.get("nonce")
    if not isinstance(nonce, str) or len(nonce) != 64:
        raise ServiceCommissioningError(
            "service commissioning request nonce is invalid"
        )
    try:
        bytes.fromhex(nonce)
    except ValueError as exc:
        raise ServiceCommissioningError(
            "service commissioning request nonce is invalid"
        ) from exc
    tags = event.tags.as_list()
    required_tags = (
        ["d", f"{REQUEST_SCHEMA}:{nonce}"],
        ["p", authority.public_key_hex(), "", "operator"],
        ["service-type", service_type],
        ["expiration", str(expires_at)],
    )
    if any(tag not in tags for tag in required_tags):
        raise ServiceCommissioningError(
            "service commissioning request is missing required tags"
        )
    if _canonical_json(content) != event.content:
        raise ServiceCommissioningError(
            "service commissioning request is not canonically encoded"
        )
    return event, content


def _create_attestation(
    request: Event,
    request_content: dict[str, Any],
    *,
    authority: Keys,
    service_type: str,
) -> dict[str, Any]:
    issued_at = max(int(time.time()), request.created_at)
    service_hex = str(request.pub_key)
    content = {
        "action": "authorize",
        "commissioning_request": request.id,
        "installation": authority.public_key_hex(),
        "issued_at": issued_at,
        "management": str(request_content["management"]),
        "previous": None,
        "relationship": "operates",
        "schema": ATTESTATION_SCHEMA,
        "schema_version": 1,
        "sequence": 1,
        "service": {"pubkey": service_hex, "type": service_type},
    }
    event = Event(
        kind=ADDRESSABLE_APPLICATION_EVENT_KIND,
        content=_canonical_json(content),
        tags=[
            ["d", f"{ATTESTATION_SCHEMA}:{service_hex}"],
            ["p", service_hex, "", "service"],
            ["e", request.id, "", "commissioning-request"],
            ["t", "mainstay-service-operator"],
            ["service-type", service_type],
        ],
        created_at=issued_at,
    )
    event.sign(authority)
    return event.data()


def _run_clear(
    arguments: list[str],
    *,
    compose_path: Path,
    env_path: Path,
    input_data: dict[str, Any] | None = None,
    uncertain_on_parse: bool = False,
) -> dict[str, Any]:
    command = [
        "docker",
        "compose",
        "--env-file",
        str(env_path),
        "-f",
        str(compose_path),
        "exec",
        "-T",
        "clear",
        "clear-root",
        *arguments,
    ]
    try:
        completed = subprocess.run(
            command,
            input=(_canonical_json(input_data) if input_data is not None else None),
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise ServiceCommissioningError(
            f"could not run Docker Compose: {exc}"
        ) from exc
    if completed.returncode != 0:
        detail = completed.stderr.strip() or "Clear service command failed"
        raise ServiceCommissioningError(detail)
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        warning = (
            "; do not retry before checking the service state"
            if uncertain_on_parse
            else ""
        )
        raise ServiceCommissioningError(
            f"Clear returned an unreadable response{warning}"
        ) from exc
    if not isinstance(result, dict):
        raise ServiceCommissioningError("Clear returned an invalid response")
    return result


def _env_value(path: Path, name: str) -> str | None:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ServiceCommissioningError(
            f"could not read environment file {path}: {exc}"
        ) from exc
    value = None
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in line:
            continue
        key, candidate = line.split("=", 1)
        if key.strip() == name:
            value = candidate.strip()
    if value and len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        value = value[1:-1]
    return value


def _canonical_json(value: dict[str, Any]) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))
