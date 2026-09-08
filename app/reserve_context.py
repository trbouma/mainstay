from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any


class ReserveContextError(RuntimeError):
    """Raised when Mainstay cannot inspect its service Acorn reserve."""


def read_service_acorn_reserve(
    *,
    compose_path: Path,
    env_path: Path | None,
) -> dict[str, Any]:
    """Read the reserve while preserving the worker's prior run state."""

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


def _run(command: list[str]) -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError as exc:
        raise ReserveContextError(f"could not run Docker Compose: {exc}") from exc


def _failure_detail(
    result: subprocess.CompletedProcess[str] | None,
    fallback: str,
) -> str:
    if result is None:
        return fallback
    return result.stderr.strip() or result.stdout.strip() or fallback
