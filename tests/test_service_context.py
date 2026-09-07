from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path
from unittest.mock import patch

import pytest
from stroma import Event, Keys

from app.cli import main
from app.service_context import (
    APPLICATION_EVENT_KIND,
    REQUEST_SCHEMA,
    ServiceCommissioningError,
    commission_service,
    installation_keys,
)

INSTALLATION_NSEC = "33" * 32
INSTALLATION_KEYS = Keys(priv_k=INSTALLATION_NSEC)
SERVICE_KEYS = Keys(priv_k="22" * 32)


def _env_file(tmp_path: Path, secret: str = INSTALLATION_NSEC) -> Path:
    path = tmp_path / ".env"
    path.write_text(f"MAINSTAY_INSTALLATION_NSEC={secret}\n", encoding="utf-8")
    return path


def _request_event() -> dict:
    issued_at = int(time.time())
    content = {
        "expires_at": issued_at + 24 * 60 * 60,
        "issued_at": issued_at,
        "management": "mainstay-managed",
        "nonce": "44" * 32,
        "requested_operator": INSTALLATION_KEYS.public_key_hex(),
        "schema": REQUEST_SCHEMA,
        "schema_version": 1,
        "service": {
            "pubkey": SERVICE_KEYS.public_key_hex(),
            "type": "clear-mint",
        },
    }
    event = Event(
        kind=APPLICATION_EVENT_KIND,
        content=json.dumps(content, sort_keys=True, separators=(",", ":")),
        tags=[
            ["d", f"{REQUEST_SCHEMA}:{content['nonce']}"],
            ["p", INSTALLATION_KEYS.public_key_hex(), "", "operator"],
            ["service-type", "clear-mint"],
            ["expiration", str(content["expires_at"])],
        ],
        created_at=issued_at,
    )
    event.sign(SERVICE_KEYS)
    return event.data()


def test_installation_identity_records_and_checks_public_sentinel(tmp_path) -> None:
    env_path = _env_file(tmp_path)
    state_path = tmp_path / "identity.json"

    first = installation_keys(env_path, state_path)
    second = installation_keys(env_path, state_path)

    assert first.public_key_bech32() == INSTALLATION_KEYS.public_key_bech32()
    assert second.public_key_bech32() == first.public_key_bech32()
    assert json.loads(state_path.read_text())["npub"] == first.public_key_bech32()
    assert state_path.stat().st_mode & 0o777 == 0o600
    assert INSTALLATION_NSEC not in state_path.read_text()


def test_installation_identity_rejects_key_replacement(tmp_path) -> None:
    env_path = _env_file(tmp_path)
    state_path = tmp_path / "identity.json"
    installation_keys(env_path, state_path)
    env_path.write_text(
        f"MAINSTAY_INSTALLATION_NSEC={'55' * 32}\n",
        encoding="utf-8",
    )

    with pytest.raises(ServiceCommissioningError, match="does not match"):
        installation_keys(env_path, state_path)


def test_commission_clear_orchestrates_signed_evidence_and_publication(
    tmp_path,
) -> None:
    env_path = _env_file(tmp_path)
    request = _request_event()
    calls = []

    def fake_run(command, **kwargs):
        calls.append((command, kwargs.get("input")))
        tail = command[command.index("clear-root") + 1 :]
        if tail[:2] == ["service", "request"]:
            payload = {"commissioning_request": request}
        elif tail == ["service", "commission"]:
            attestation = json.loads(kwargs["input"])
            event = Event.load(attestation, validate=True)
            assert event is not None
            assert event.pub_key == INSTALLATION_KEYS.public_key_hex()
            payload = {
                "service_identity": {
                    "state": "commissioned",
                    "npub": SERVICE_KEYS.public_key_bech32(),
                },
                "service_descriptor": {"id": "descriptor-id"},
            }
        elif tail == ["service", "verify"]:
            attestation = Event.load(json.loads(calls[-2][1]), validate=True)
            assert attestation is not None
            payload = {
                "state": "commissioned",
                "service_key_control": "verified",
                "operator_authorship": "verified",
                "reciprocal_relationship": "verified",
                "operator_npub": INSTALLATION_KEYS.public_key_bech32(),
                "commissioning_request_event_id": request["id"],
                "operator_attestation_event_id": attestation.id,
                "service_descriptor_event_id": "descriptor-id",
            }
        elif tail == [
            "service",
            "publish",
            "--relay",
            "ws://spurline:8080",
        ]:
            payload = {"state": "published"}
        else:
            raise AssertionError(tail)
        return subprocess.CompletedProcess(
            args=command,
            returncode=0,
            stdout=json.dumps(payload),
            stderr="",
        )

    with patch("app.service_context.subprocess.run", side_effect=fake_run):
        result = commission_service(
            "clear",
            compose_path=Path("docker-compose.yaml"),
            env_path=env_path,
            state_path=tmp_path / "identity.json",
            relay="ws://spurline:8080",
        )

    assert result["state"] == "commissioned"
    assert result["service_npub"] == SERVICE_KEYS.public_key_bech32()
    assert result["installation_npub"] == INSTALLATION_KEYS.public_key_bech32()
    assert result["publication"] == {"state": "published"}
    assert len(calls) == 4
    assert all(INSTALLATION_NSEC not in " ".join(call[0]) for call in calls)
    assert all(INSTALLATION_NSEC not in (call[1] or "") for call in calls)


def test_commission_rejects_service_outside_supported_registry(tmp_path) -> None:
    with (
        patch("app.service_context.subprocess.run") as run,
        pytest.raises(ServiceCommissioningError, match="currently supported: clear"),
    ):
        commission_service(
            "grove",
            compose_path=Path("docker-compose.yaml"),
            env_path=_env_file(tmp_path),
            state_path=tmp_path / "identity.json",
            relay="ws://spurline:8080",
        )

    run.assert_not_called()


def test_service_cli_uses_managed_relay_and_clear_target() -> None:
    with (
        patch(
            "app.cli.commission_service",
            return_value={"state": "commissioned"},
        ) as commission,
        patch("builtins.print"),
    ):
        result = main(
            [
                "service",
                "commission",
                "clear",
                "--env-file",
                ".env",
            ]
        )

    assert result == 0
    assert commission.call_args.args == ("clear",)
    assert commission.call_args.kwargs["relay"] == "ws://spurline:8080"
    assert commission.call_args.kwargs["env_path"] == Path(".env")
    assert commission.call_args.kwargs["publish"] is True
