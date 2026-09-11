from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

REPOSITORY = Path(__file__).parents[1]


def test_fresh_start_prepares_environment_and_waits_for_readiness(tmp_path) -> None:
    deployment = tmp_path / "mainstay"
    deployment.mkdir()
    for name in (
        ".env.example",
        "docker-compose.yaml",
        "init-env.sh",
        "save-recovery-env.sh",
        "start-mainstay.sh",
    ):
        shutil.copy2(REPOSITORY / name, deployment / name)

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    docker_log = tmp_path / "docker.log"
    docker = fake_bin / "docker"
    docker.write_text(
        """#!/bin/sh
printf '%s\n' "$*" >> "$DOCKER_LOG"
case "$*" in
  "volume inspect "*) exit 1 ;;
  "compose ps -q service-acorn-worker") printf '%s\n' worker-id ;;
  "inspect --format "*) printf '%s\n' healthy ;;
esac
exit 0
""",
        encoding="utf-8",
    )
    docker.chmod(docker.stat().st_mode | stat.S_IXUSR)
    ss = fake_bin / "ss"
    ss.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    ss.chmod(ss.stat().st_mode | stat.S_IXUSR)

    environment = os.environ.copy()
    environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
    environment["DOCKER_LOG"] = str(docker_log)
    result = subprocess.run(
        [str(deployment / "start-mainstay.sh"), "--no-build"],
        cwd=deployment,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "Created .env with generated Mainstay secrets." in result.stdout
    assert "Mainstay is ready." in result.stdout
    assert "Dashboard: http://127.0.0.1:8788/" in result.stdout
    env_text = (deployment / ".env").read_text(encoding="utf-8")
    assert "MAINSTAY_INSTALLATION_NSEC=" in env_text
    assert "CLEAR_MASTER_SECRET=" in env_text
    assert stat.S_IMODE((deployment / ".env").stat().st_mode) == 0o600

    commands = docker_log.read_text(encoding="utf-8")
    assert "compose version" in commands
    assert "compose config --quiet" in commands
    assert "compose up --detach" in commands
    assert "compose exec -T mainstay-local" in commands
    assert "inspect --format {{.State.Health.Status}} worker-id" in commands


def test_start_rejects_a_host_port_owned_by_another_project(
    tmp_path: Path,
) -> None:
    deployment = tmp_path / "mainstay"
    deployment.mkdir()
    for name in (
        ".env.example",
        "docker-compose.yaml",
        "init-env.sh",
        "save-recovery-env.sh",
        "start-mainstay.sh",
    ):
        shutil.copy2(REPOSITORY / name, deployment / name)

    env_text = (deployment / ".env.example").read_text(encoding="utf-8")
    env_text = env_text.replace(
        "COMPOSE_PROJECT_NAME=mainstay-local",
        "COMPOSE_PROJECT_NAME=mainstay-test",
    ).replace("MAINSTAY_LOCAL_PORT=8788", "MAINSTAY_LOCAL_PORT=9001")
    (deployment / ".env").write_text(env_text, encoding="utf-8")

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    docker_log = tmp_path / "docker.log"
    docker = fake_bin / "docker"
    docker.write_text(
        """#!/bin/sh
printf '%s\n' "$*" >> "$DOCKER_LOG"
case "$*" in
    "volume inspect "*) exit 1 ;;
esac
if [ "$1" = "ps" ]; then
    case "$*" in
        *"publish=9001"*)
            printf '%s\n' \
                'mainstay-other-mainstay-local-1|mainstay-other|mainstay-local'
            ;;
    esac
fi
exit 0
""",
        encoding="utf-8",
    )
    docker.chmod(docker.stat().st_mode | stat.S_IXUSR)
    ss = fake_bin / "ss"
    ss.write_text(
        """#!/bin/sh
printf '%s\n' 'LISTEN 0 128 0.0.0.0:9001 0.0.0.0:*'
""",
        encoding="utf-8",
    )
    ss.chmod(ss.stat().st_mode | stat.S_IXUSR)

    environment = os.environ.copy()
    environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
    environment["DOCKER_LOG"] = str(docker_log)
    result = subprocess.run(
        [str(deployment / "start-mainstay.sh"), "--no-build"],
        cwd=deployment,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Dashboard host port 9001 is already published by" in result.stderr
    assert "mainstay-other-mainstay-local-1 (project mainstay-other)" in (
        result.stderr
    )
    assert "Set MAINSTAY_LOCAL_PORT to an unused host port" in result.stderr
    commands = docker_log.read_text(encoding="utf-8")
    assert "compose config --quiet" in commands
    assert "compose up" not in commands


def test_refresh_delegates_to_the_canonical_start_path() -> None:
    script = (REPOSITORY / "refresh-containers.sh").read_text(encoding="utf-8")

    assert 'exec "$repo_dir/start-mainstay.sh" --force-recreate "$@"' in script
