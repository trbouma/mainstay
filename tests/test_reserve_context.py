from __future__ import annotations

import json
import subprocess
from pathlib import Path
from unittest.mock import patch

import pytest

from app.cli import main
from app.reserve_context import ReserveContextError, read_service_acorn_reserve


class FakeResponse:
    status = 200

    def __init__(self, payload: dict[str, object]) -> None:
        self.body = json.dumps(payload).encode()

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self) -> bytes:
        return self.body


def completed(
    *,
    returncode: int = 0,
    stdout: str = "",
    stderr: str = "",
) -> subprocess.CompletedProcess[str]:
    return subprocess.CompletedProcess([], returncode, stdout, stderr)


def test_balance_pauses_and_restarts_a_running_worker() -> None:
    payload = {
        "status": "OK",
        "balance": 457,
        "unit": "sat",
        "mint": "https://mint.example.com",
        "npub": "npub1service",
    }
    responses = [
        completed(stdout="container-id\n"),
        completed(),
        completed(stdout=json.dumps(payload)),
        completed(),
    ]

    with patch("app.reserve_context.subprocess.run", side_effect=responses) as run:
        result = read_service_acorn_reserve(
            compose_path=Path("docker-compose.yaml"),
            env_path=Path(".env"),
        )

    assert result["balance"] == 457
    assert result["worker_restarted"] is True
    commands = [call.args[0] for call in run.call_args_list]
    assert commands[0][-5:] == [
        "ps",
        "--status",
        "running",
        "--quiet",
        "service-acorn-worker",
    ]
    assert commands[1][-2:] == ["stop", "service-acorn-worker"]
    assert commands[2][-5:] == [
        "python",
        "-m",
        "app.service_acorn_worker",
        "balance",
        "--json",
    ]
    assert commands[3][-4:] == [
        "up",
        "-d",
        "--no-deps",
        "service-acorn-worker",
    ]


def test_balance_prefers_safebox_management_endpoint() -> None:
    payload = {
        "status": "OK",
        "balance": 457,
        "unit": "sat",
        "mint": "https://mint.example.com",
        "npub": "npub1service",
        "updated_at": 123456,
    }
    with (
        patch.dict(
            "os.environ",
            {
                "MAINSTAY_SAFEBOX_MANAGEMENT_URL": "http://safebox-web:8000",
                "SAFEBOX_MANAGEMENT_TOKEN": "management-token",
            },
        ),
        patch(
            "app.reserve_context.urlopen",
            return_value=FakeResponse(payload),
        ) as open_url,
        patch("app.reserve_context.subprocess.run") as run,
    ):
        result = read_service_acorn_reserve(
            compose_path=Path("docker-compose.yaml"),
            env_path=Path(".env"),
        )

    assert result["balance"] == 457
    assert result["worker_restarted"] is False
    request = open_url.call_args.args[0]
    assert request.full_url == (
        "http://safebox-web:8000/internal/service-acorn/reserve"
    )
    assert request.headers["Authorization"] == "Bearer management-token"
    run.assert_not_called()


def test_balance_does_not_start_a_worker_that_was_stopped() -> None:
    responses = [
        completed(stdout=""),
        completed(stdout='{"status":"OK","balance":12}'),
    ]

    with patch("app.reserve_context.subprocess.run", side_effect=responses) as run:
        result = read_service_acorn_reserve(
            compose_path=Path("compose.yaml"),
            env_path=None,
        )

    assert result["worker_restarted"] is False
    assert len(run.call_args_list) == 2


def test_balance_failure_still_restarts_running_worker() -> None:
    responses = [
        completed(stdout="container-id\n"),
        completed(),
        completed(returncode=1, stderr="wallet unavailable"),
        completed(),
    ]

    with (
        patch("app.reserve_context.subprocess.run", side_effect=responses) as run,
        pytest.raises(ReserveContextError, match="wallet unavailable"),
    ):
        read_service_acorn_reserve(
            compose_path=Path("compose.yaml"),
            env_path=Path("venue.env"),
        )

    assert run.call_args_list[-1].args[0][-4:] == [
        "up",
        "-d",
        "--no-deps",
        "service-acorn-worker",
    ]


def test_balance_reports_host_side_command_when_docker_is_unavailable() -> None:
    with (
        patch(
            "app.reserve_context.subprocess.run",
            side_effect=FileNotFoundError(2, "No such file or directory", "docker"),
        ),
        pytest.raises(ReserveContextError, match="./reserve-balance.sh"),
    ):
        read_service_acorn_reserve(
            compose_path=Path("compose.yaml"),
            env_path=Path(".env"),
        )


def test_mainstay_cli_reports_reserve_balance(capsys) -> None:
    with patch(
        "app.cli.read_service_acorn_reserve",
        return_value={"balance": 457},
    ) as read:
        result = main(
            [
                "reserve",
                "balance",
                "--compose-file",
                "venue.yaml",
                "--env-file",
                "venue.env",
            ]
        )

    assert result == 0
    assert capsys.readouterr().out == "Service Acorn reserve: 457 sats\n"
    read.assert_called_once_with(
        compose_path=Path("venue.yaml"),
        env_path=Path("venue.env"),
    )
