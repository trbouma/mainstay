from __future__ import annotations

import io
import json
import subprocess
from pathlib import Path
from unittest.mock import patch
from urllib.error import HTTPError

import pytest

from app.cli import main
from app.reserve_context import (
    ReserveContextError,
    fund_service_acorn_reserve,
    read_service_acorn_reserve,
)


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


def test_fund_reserve_prints_invoice_qr(capsys) -> None:
    calls: list[tuple] = []

    class FakeQr:
        def add_data(self, invoice):
            calls.append(("qr-data", invoice))

        def make(self, *, fit):
            calls.append(("qr-make", fit))

        def print_ascii(self):
            print("ASCII QR")

    responses = [
        FakeResponse({"id": "funding-1", "status": "REQUESTED", "amount": 21}),
        FakeResponse(
            {
                "id": "funding-1",
                "status": "PENDING",
                "amount": 21,
                "mint": "https://mint.example.com",
                "invoice": "lnbc123",
            }
        ),
        FakeResponse(
            {
                "id": "funding-1",
                "status": "CONFIRMED",
                "amount": 21,
                "balance": 33,
            }
        ),
    ]
    with (
        patch.dict(
            "os.environ",
            {
                "MAINSTAY_SAFEBOX_MANAGEMENT_URL": "http://safebox-web:8000",
                "SAFEBOX_MANAGEMENT_TOKEN": "management-token",
            },
        ),
        patch("app.reserve_context.urlopen", side_effect=responses),
        patch("app.reserve_context.qrcode.QRCode", FakeQr),
        patch("app.reserve_context.time.sleep"),
    ):
        result = fund_service_acorn_reserve(
            amount=21,
            mint=None,
            compose_path=Path("docker-compose.yaml"),
            env_path=Path(".env"),
        )

    assert result["status"] == "CONFIRMED"
    assert ("qr-data", "lnbc123") in calls
    assert ("qr-make", True) in calls
    output = capsys.readouterr().out
    assert "Invoice:\nlnbc123" in output
    assert "QR code:\nASCII QR" in output


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
        patch("app.reserve_context._running_in_container", return_value=False),
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


def test_balance_requires_management_env_inside_container() -> None:
    with (
        patch.dict("os.environ", {}, clear=True),
        patch("app.reserve_context._running_in_container", return_value=True),
        pytest.raises(ReserveContextError, match="MAINSTAY_SAFEBOX_MANAGEMENT_URL"),
    ):
        read_service_acorn_reserve(
            compose_path=Path("compose.yaml"),
            env_path=Path(".env"),
        )


def test_balance_reports_missing_safebox_endpoint_inside_container() -> None:
    error = HTTPError(
        "http://safebox-web:8000/internal/service-acorn/reserve",
        404,
        "Not Found",
        {},
        io.BytesIO(b'{"detail":"Not found"}'),
    )
    with (
        patch.dict(
            "os.environ",
            {
                "MAINSTAY_SAFEBOX_MANAGEMENT_URL": "http://safebox-web:8000",
                "SAFEBOX_MANAGEMENT_TOKEN": "management-token",
            },
        ),
        patch("app.reserve_context._running_in_container", return_value=True),
        patch("app.reserve_context.urlopen", side_effect=error),
        pytest.raises(ReserveContextError, match="Safebox reserve endpoint"),
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


def test_mainstay_cli_funds_reserve(capsys) -> None:
    with patch(
        "app.cli.fund_service_acorn_reserve",
        return_value={"status": "CONFIRMED", "amount": 21, "balance": 33},
    ) as fund:
        result = main(
            [
                "reserve",
                "fund",
                "21",
                "--mint",
                "https://mint.example.com",
                "--compose-file",
                "venue.yaml",
                "--env-file",
                "venue.env",
            ]
        )

    assert result == 0
    assert capsys.readouterr().out == (
        "Service Acorn reserve funding confirmed: "
        "21 sats deposited; balance=33 sats\n"
    )
    fund.assert_called_once_with(
        amount=21,
        mint="https://mint.example.com",
        compose_path=Path("venue.yaml"),
        env_path=Path("venue.env"),
    )
