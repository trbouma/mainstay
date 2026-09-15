from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class ReserveContextError(RuntimeError):
    """Raised when Mainstay cannot inspect its service Acorn reserve."""


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
    try:
        with urlopen(request, timeout=5) as response:
            body = response.read()
    except HTTPError as exc:
        detail = exc.read().decode(errors="replace")
        raise ReserveContextError(
            f"Safebox reserve endpoint returned HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise ReserveContextError(
            f"Safebox reserve endpoint is unavailable: {exc.reason}"
        ) from exc
    try:
        result = json.loads(body)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ReserveContextError(
            "Safebox reserve endpoint returned unreadable JSON"
        ) from exc
    if not isinstance(result, dict) or not isinstance(result.get("balance"), int):
        raise ReserveContextError(
            "Safebox reserve endpoint returned an incomplete reserve balance"
        )
    result["worker_restarted"] = False
    return result


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
