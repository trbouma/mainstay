from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path


PROJECT_ROOT = Path(__file__).parents[1]


def test_reserve_balance_uses_compose_and_restores_running_worker(
    tmp_path: Path,
) -> None:
    script = tmp_path / "reserve-balance.sh"
    shutil.copy2(PROJECT_ROOT / "reserve-balance.sh", script)
    (tmp_path / ".env").write_text(
        "COMPOSE_PROJECT_NAME=private-venue\n", encoding="utf-8"
    )
    (tmp_path / "docker-compose.yaml").write_text("services: {}\n", encoding="utf-8")
    docker_log = tmp_path / "docker.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    docker = bin_dir / "docker"
    docker.write_text(
        """#!/bin/sh
printf '%s\n' "$*" >> "$DOCKER_LOG"
case "$*" in
  "compose version") exit 0 ;;
  *" ps --status running --quiet service-acorn-worker")
    printf '%s\n' worker-id
    exit 0
    ;;
  *" run --rm --no-deps service-acorn-worker python -m app.service_acorn_worker balance")
    printf '%s\n' 'Service Acorn reserve: 457 sats'
    exit 0
    ;;
esac
exit 0
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    environment = os.environ.copy()
    environment["PATH"] = f"{bin_dir}:{environment['PATH']}"
    environment["DOCKER_LOG"] = str(docker_log)

    result = subprocess.run(
        [str(script)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert result.stdout == "Service Acorn reserve: 457 sats\n"
    commands = docker_log.read_text(encoding="utf-8")
    assert " stop service-acorn-worker" in commands
    assert " run --rm --no-deps service-acorn-worker" in commands
    assert " up -d --no-deps service-acorn-worker" in commands


def test_reserve_balance_leaves_a_stopped_worker_stopped(tmp_path: Path) -> None:
    script = tmp_path / "reserve-balance.sh"
    shutil.copy2(PROJECT_ROOT / "reserve-balance.sh", script)
    (tmp_path / ".env").write_text("COMPOSE_PROJECT_NAME=test\n", encoding="utf-8")
    (tmp_path / "docker-compose.yaml").write_text("services: {}\n", encoding="utf-8")
    docker_log = tmp_path / "docker.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    docker = bin_dir / "docker"
    docker.write_text(
        """#!/bin/sh
printf '%s\n' "$*" >> "$DOCKER_LOG"
case "$*" in
  "compose version") exit 0 ;;
  *" run --rm --no-deps service-acorn-worker python -m app.service_acorn_worker balance")
    printf '%s\n' 'Service Acorn reserve: 0 sats'
    exit 0
    ;;
esac
exit 0
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    environment = os.environ.copy()
    environment["PATH"] = f"{bin_dir}:{environment['PATH']}"
    environment["DOCKER_LOG"] = str(docker_log)

    result = subprocess.run(
        [str(script)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    commands = docker_log.read_text(encoding="utf-8")
    assert " stop service-acorn-worker" not in commands
    assert " up -d --no-deps service-acorn-worker" not in commands


def test_reserve_balance_restores_worker_after_balance_failure(tmp_path: Path) -> None:
    script = tmp_path / "reserve-balance.sh"
    shutil.copy2(PROJECT_ROOT / "reserve-balance.sh", script)
    (tmp_path / ".env").write_text("COMPOSE_PROJECT_NAME=test\n", encoding="utf-8")
    (tmp_path / "docker-compose.yaml").write_text("services: {}\n", encoding="utf-8")
    docker_log = tmp_path / "docker.log"
    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    docker = bin_dir / "docker"
    docker.write_text(
        """#!/bin/sh
printf '%s\n' "$*" >> "$DOCKER_LOG"
case "$*" in
  "compose version") exit 0 ;;
  *" ps --status running --quiet service-acorn-worker")
    printf '%s\n' worker-id
    exit 0
    ;;
  *" run --rm --no-deps service-acorn-worker python -m app.service_acorn_worker balance")
    exit 1
    ;;
esac
exit 0
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    environment = os.environ.copy()
    environment["PATH"] = f"{bin_dir}:{environment['PATH']}"
    environment["DOCKER_LOG"] = str(docker_log)

    result = subprocess.run(
        [str(script)],
        cwd=tmp_path,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    commands = docker_log.read_text(encoding="utf-8")
    assert " stop service-acorn-worker" in commands
    assert " up -d --no-deps service-acorn-worker" in commands
