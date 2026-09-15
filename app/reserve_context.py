from __future__ import annotations

import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import qrcode


class ReserveContextError(RuntimeError):
    """Raised when Mainstay cannot inspect its service Acorn reserve."""


def fund_service_acorn_reserve(
    *,
    amount: int,
    mint: str | None,
    compose_path: Path,
    env_path: Path | None,
    poll_interval_seconds: float = 2.0,
) -> dict[str, Any]:
    """Fund the reserve through the container-native management endpoint."""

    if amount <= 0:
        raise ReserveContextError("reserve funding amount must be greater than zero")
    management_url = os.getenv("MAINSTAY_SAFEBOX_MANAGEMENT_URL", "").strip()
    management_token = os.getenv("SAFEBOX_MANAGEMENT_TOKEN", "").strip()
    if management_url and management_token:
        funding = _create_service_acorn_reserve_funding_api(
            management_url,
            management_token=management_token,
            amount=amount,
            mint=mint,
        )
        funding_id = str(funding.get("id") or "")
        if not funding_id:
            raise ReserveContextError(
                "Safebox reserve funding endpoint returned no funding id"
            )
        return _poll_service_acorn_reserve_funding_api(
            management_url,
            management_token=management_token,
            funding_id=funding_id,
            poll_interval_seconds=poll_interval_seconds,
        )
    if _running_in_container():
        raise ReserveContextError(
            "container-native reserve funding is not configured; recreate the "
            "mainstay-local container from the updated Compose file after "
            "running ./init-env.sh."
        )
    return _fund_service_acorn_reserve_compose(
        amount=amount,
        mint=mint,
        compose_path=compose_path,
        env_path=env_path,
    )


def read_service_acorn_reserve(
    *,
    compose_path: Path,
    env_path: Path | None,
) -> dict[str, Any]:
    """Read the reserve while preserving the worker's prior run state."""

    management_url = os.getenv("MAINSTAY_SAFEBOX_MANAGEMENT_URL", "").strip()
    management_token = os.getenv("SAFEBOX_MANAGEMENT_TOKEN", "").strip()
    if management_url and management_token:
        try:
            return _read_service_acorn_reserve_api(
                management_url,
                management_token=management_token,
            )
        except ReserveContextError as exc:
            if "HTTP 404" in str(exc):
                if _running_in_container():
                    raise ReserveContextError(
                        "Safebox reserve endpoint is not available. Rebuild "
                        "safebox-web with the internal service-Acorn reserve "
                        "endpoint before using container-native reserve checks."
                    ) from exc
            else:
                raise
    elif _running_in_container():
        missing = []
        if not management_url:
            missing.append("MAINSTAY_SAFEBOX_MANAGEMENT_URL")
        if not management_token:
            missing.append("SAFEBOX_MANAGEMENT_TOKEN")
        raise ReserveContextError(
            "container-native reserve check is not configured; missing "
            f"{', '.join(missing)}. Recreate the mainstay-local container from "
            "the updated Compose file after running ./init-env.sh."
        )

    prefix = ["docker", "compose"]
    if env_path is not None:
        prefix.extend(["--env-file", str(env_path)])
    prefix.extend(["-f", str(compose_path)])

    status = _run(
        [*prefix, "ps", "--status", "running", "--quiet", "service-acorn-worker"]
    )
    if status.returncode != 0:
        raise ReserveContextError(_failure_detail(status, "could not inspect worker"))
    was_running = bool(status.stdout.strip())

    if was_running:
        stopped = _run([*prefix, "stop", "service-acorn-worker"])
        if stopped.returncode != 0:
            raise ReserveContextError(
                _failure_detail(stopped, "could not pause service Acorn worker")
            )

    balance_result: subprocess.CompletedProcess[str] | None = None
    restart_result: subprocess.CompletedProcess[str] | None = None
    try:
        balance_result = _run(
            [
                *prefix,
                "run",
                "--rm",
                "--no-deps",
                "service-acorn-worker",
                "python",
                "-m",
                "app.service_acorn_worker",
                "balance",
                "--json",
            ]
        )
    finally:
        if was_running:
            restart_result = _run(
                [*prefix, "up", "-d", "--no-deps", "service-acorn-worker"]
            )

    if balance_result is None or balance_result.returncode != 0:
        detail = _failure_detail(
            balance_result,
            "could not read service Acorn reserve",
        )
        if restart_result is not None and restart_result.returncode != 0:
            detail += "; the service Acorn worker also failed to restart"
        raise ReserveContextError(detail)
    if restart_result is not None and restart_result.returncode != 0:
        raise ReserveContextError(
            _failure_detail(
                restart_result,
                "reserve was read but the service Acorn worker failed to restart",
            )
        )

    try:
        result = json.loads(balance_result.stdout)
    except json.JSONDecodeError as exc:
        raise ReserveContextError(
            "service Acorn returned an unreadable reserve balance"
        ) from exc
    if not isinstance(result, dict) or not isinstance(result.get("balance"), int):
        raise ReserveContextError(
            "service Acorn returned an incomplete reserve balance"
        )
    result["worker_restarted"] = was_running
    return result


def _create_service_acorn_reserve_funding_api(
    base_url: str,
    *,
    management_token: str,
    amount: int,
    mint: str | None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"amount": amount}
    if mint:
        payload["mint"] = mint
    request = Request(
        f"{base_url.rstrip('/')}/internal/service-acorn/reserve/funding",
        data=json.dumps(payload).encode(),
        method="POST",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {management_token}",
            "Content-Type": "application/json",
            "User-Agent": "mainstayctl",
        },
    )
    return _reserve_api_json(request, "Safebox reserve funding endpoint")


def _poll_service_acorn_reserve_funding_api(
    base_url: str,
    *,
    management_token: str,
    funding_id: str,
    poll_interval_seconds: float,
) -> dict[str, Any]:
    invoice_shown = False
    deadline = time.time() + 300
    while True:
        request = Request(
            f"{base_url.rstrip('/')}/internal/service-acorn/reserve/funding/{funding_id}",
            headers={
                "Accept": "application/json",
                "Authorization": f"Bearer {management_token}",
                "User-Agent": "mainstayctl",
            },
        )
        result = _reserve_api_json(request, "Safebox reserve funding endpoint")
        status = str(result.get("status") or "").upper()
        invoice = str(result.get("invoice") or "")
        if invoice and not invoice_shown:
            print(f"Service Acorn funding amount: {result.get('amount')} sats")
            print(f"Mint: {result.get('mint')}")
            print(f"Invoice:\n{invoice}\n")
            _print_invoice_qr(invoice)
            print("Waiting for payment confirmation. Keep this command running...")
            invoice_shown = True
        if status == "CONFIRMED":
            return result
        if status in {"EXPIRED", "FAILED"}:
            detail = str(result.get("detail") or "reserve funding failed")
            raise ReserveContextError(detail)
        if time.time() >= deadline:
            raise ReserveContextError(
                "timed out waiting for service Acorn funding confirmation"
            )
        time.sleep(max(0.2, poll_interval_seconds))


def _print_invoice_qr(invoice: str) -> None:
    qr = qrcode.QRCode()
    qr.add_data(invoice)
    qr.make(fit=True)
    print("QR code:")
    qr.print_ascii()


def _read_service_acorn_reserve_api(
    base_url: str,
    *,
    management_token: str,
) -> dict[str, Any]:
    request = Request(
        f"{base_url.rstrip('/')}/internal/service-acorn/reserve",
        headers={
            "Accept": "application/json",
            "Authorization": f"Bearer {management_token}",
            "User-Agent": "mainstayctl",
        },
    )
    result = _reserve_api_json(request, "Safebox reserve endpoint")
    if not isinstance(result, dict) or not isinstance(result.get("balance"), int):
        raise ReserveContextError(
            "Safebox reserve endpoint returned an incomplete reserve balance"
        )
    result["worker_restarted"] = False
    return result


def _reserve_api_json(request: Request, label: str) -> dict[str, Any]:
    try:
        with urlopen(request, timeout=5) as response:
            body = response.read()
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise ReserveContextError(
            f"{label} returned HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise ReserveContextError(f"{label} is unavailable: {exc.reason}") from exc
    try:
        result = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReserveContextError(f"{label} returned unreadable JSON") from exc
    if not isinstance(result, dict):
        raise ReserveContextError(f"{label} returned an unexpected response")
    return result


def _fund_service_acorn_reserve_compose(
    *,
    amount: int,
    mint: str | None,
    compose_path: Path,
    env_path: Path | None,
) -> dict[str, Any]:
    prefix = ["docker", "compose"]
    if env_path is not None:
        prefix.extend(["--env-file", str(env_path)])
    command = [
        *prefix,
        "-f",
        str(compose_path),
        "run",
        "--rm",
        "--no-deps",
        "service-acorn-worker",
        "python",
        "-m",
        "app.service_acorn_worker",
        "fund",
        str(amount),
    ]
    if mint:
        command.extend(["--mint", mint])
    result = _run(command)
    if result.returncode != 0:
        raise ReserveContextError(
            _failure_detail(result, "could not fund service Acorn reserve")
        )
    return {"status": "CONFIRMED", "amount": amount}


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        if exc.filename == "docker":
            raise ReserveContextError(
                "Docker is not available in this container. Run the reserve "
                "check from the deployment host with `./reserve-balance.sh` or "
                "`poetry run mainstayctl reserve balance`."
            ) from exc
        raise ReserveContextError(f"could not run Docker Compose: {exc}") from exc


def _running_in_container() -> bool:
    return Path("/.dockerenv").exists() or Path("/run/.containerenv").exists()


def _failure_detail(
    result: subprocess.CompletedProcess[str] | None,
    fallback: str,
) -> str:
    if result is None:
        return fallback
    return result.stderr.strip() or result.stdout.strip() or fallback
