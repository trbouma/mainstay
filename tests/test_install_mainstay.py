from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]


def _stage_installer(tmp_path: Path) -> tuple[Path, dict[str, str], Path]:
    deployment = tmp_path / "mainstay"
    deployment.mkdir()
    for name in (
        ".env.example",
        "docker-compose.yaml",
        "init-env.sh",
        "install-mainstay.sh",
        "save-recovery-env.sh",
        "start-mainstay.sh",
        "teardown-mainstay.sh",
    ):
        shutil.copy2(PROJECT_ROOT / name, deployment / name)

    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    docker_log = tmp_path / "docker.log"
    docker = fake_bin / "docker"
    docker.write_text(
        """#!/bin/sh
printf '%s\n' "$*" >> "$DOCKER_LOG"
if [ "$1" = "info" ]; then exit 0; fi
if [ "$1" = "compose" ] && [ "$2" = "version" ]; then exit 0; fi
if [ "$1" = "ps" ] && [ "${MOCK_PROJECT_EXISTS:-0}" = "1" ]; then
    printf '%s\n' existing-container
    exit 0
fi
if [ "$1" = "volume" ] && [ "$2" = "inspect" ]; then exit 1; fi
if [ "$1" = "compose" ] && [ "$2" = "down" ]; then exit 0; fi
exit 0
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    ss = fake_bin / "ss"
    ss.write_text(
        """#!/bin/sh
if [ -n "${MOCK_LISTEN_PORT:-}" ]; then
    printf 'LISTEN 0 128 0.0.0.0:%s 0.0.0.0:*\n' "$MOCK_LISTEN_PORT"
fi
""",
        encoding="utf-8",
    )
    ss.chmod(0o755)

    environment = os.environ.copy()
    environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
    environment["DOCKER_LOG"] = str(docker_log)
    return deployment, environment, docker_log


def _read_env(path: Path) -> dict[str, str]:
    return {
        key: value
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#") and "=" in line
        for key, value in [line.split("=", 1)]
    }


def test_installer_uses_shipped_defaults_and_can_configure_without_starting(
    tmp_path: Path,
) -> None:
    deployment, environment, _docker_log = _stage_installer(tmp_path)
    answers = "mainstay-testlab\n" + "\n" * 5 + "no\nyes\n"

    result = subprocess.run(
        [str(deployment / "install-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input=answers,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "each Mainstay instance from its own dedicated deployment directory" in (
        result.stdout
    )
    values = _read_env(deployment / ".env")
    data_parent = deployment / ".mainstay-data"
    data_root = data_parent / "mainstay-testlab"
    assert values["COMPOSE_PROJECT_NAME"] == "mainstay-testlab"
    assert values["MAINSTAY_DATA_PARENT"] == str(data_parent)
    assert values["MAINSTAY_DATA_DIRECTORY_NAME"] == "mainstay-testlab"
    assert values["MAINSTAY_DATA_ROOT"] == str(data_root)
    assert values["MAINSTAY_LOCAL_BIND_ADDRESS"] == "0.0.0.0"
    assert values["MAINSTAY_LOCAL_PORT"] == "8788"
    assert values["MAINSTAY_SAFEBOX_BIND_ADDRESS"] == "0.0.0.0"
    assert values["MAINSTAY_SAFEBOX_PORT"] == "8888"
    assert (
        data_root / ".mainstay-local-managed-data-root"
    ).read_text(encoding="utf-8") == "org.mainstay.local-managed-data-root:v1\n"
    recovery_file = data_root / ".env.recovery"
    assert recovery_file.read_text(encoding="utf-8") == (
        deployment / ".env"
    ).read_text(encoding="utf-8")
    assert recovery_file.stat().st_mode & 0o777 == 0o600
    assert "Run ./start-mainstay.sh when you are ready." in result.stdout
    assert "Preflight checks passed. No configuration has been written." in (
        result.stdout
    )


def test_installer_can_abort_before_changing_files(tmp_path: Path) -> None:
    deployment, environment, _docker_log = _stage_installer(tmp_path)

    result = subprocess.run(
        [str(deployment / "install-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input="abort\n",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 130
    assert "No changes were made" in result.stderr
    assert not (deployment / ".env").exists()
    assert not (deployment / ".mainstay-data").exists()


def test_installer_rejects_an_occupied_selected_port_before_writing(
    tmp_path: Path,
) -> None:
    deployment, environment, _docker_log = _stage_installer(tmp_path)
    environment["MOCK_LISTEN_PORT"] = "9001"
    data_parent = deployment / "data"
    answers = f"port-test\n{data_parent}\n\n9001\n\n9000\nyes\n"

    result = subprocess.run(
        [str(deployment / "install-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input=answers,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "Dashboard port 9001 is already in use" in result.stderr
    assert not (deployment / ".env").exists()
    assert not data_parent.exists()


def test_installer_rejects_an_existing_compose_project_before_writing(
    tmp_path: Path,
) -> None:
    deployment, environment, _docker_log = _stage_installer(tmp_path)
    environment["MOCK_PROJECT_EXISTS"] = "1"
    answers = "mainstay-local\n" + "\n" * 5 + "yes\n"

    result = subprocess.run(
        [str(deployment / "install-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input=answers,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "already has containers on this host" in result.stderr
    assert not (deployment / ".env").exists()


def test_existing_env_values_are_displayed_as_defaults_without_mutation(
    tmp_path: Path,
) -> None:
    deployment, environment, _docker_log = _stage_installer(tmp_path)
    env_file = deployment / ".env"
    original = (
        "COMPOSE_PROJECT_NAME=private-venue\n"
        "MAINSTAY_DATA_ROOT=\n"
        "MAINSTAY_LOCAL_BIND_ADDRESS=127.0.0.1\n"
        "MAINSTAY_LOCAL_PORT=9876\n"
        "MAINSTAY_SAFEBOX_BIND_ADDRESS=100.70.55.66\n"
        "MAINSTAY_SAFEBOX_PORT=9999\n"
    )
    env_file.write_text(original, encoding="utf-8")

    result = subprocess.run(
        [str(deployment / "install-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input="\n\n\n\n\n\nno\nno\n",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 130
    assert "Compose project name [private-venue]" in result.stderr
    assert "Dashboard host port [9876]" in result.stderr
    assert "Safebox Web host port [9999]" in result.stderr
    assert env_file.read_text(encoding="utf-8") == original


def test_teardown_removes_installer_managed_data_and_configuration(
    tmp_path: Path,
) -> None:
    deployment, environment, docker_log = _stage_installer(tmp_path)
    data_root = deployment / ".mainstay-data"
    data_root.mkdir()
    (data_root / ".mainstay-local-managed-data-root").write_text(
        "org.mainstay.local-managed-data-root:v1\n",
        encoding="utf-8",
    )
    (data_root / "clear").mkdir()
    (data_root / "clear" / "clear.sqlite3").write_text(
        "state",
        encoding="utf-8",
    )
    (deployment / ".env").write_text(
        f"MAINSTAY_DATA_ROOT={data_root}\n",
        encoding="utf-8",
    )
    identity_state = deployment / "build/mainstay-local"
    identity_state.mkdir(parents=True)
    (identity_state / "installation-identity.json").write_text(
        "{}\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [str(deployment / "teardown-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input="DELETE\n",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert "owned by this deployment directory" in result.stdout
    assert not data_root.exists()
    assert not (deployment / ".env").exists()
    assert not identity_state.exists()
    assert "compose down --volumes --remove-orphans" in docker_log.read_text(
        encoding="utf-8"
    )


def test_teardown_preserves_unmarked_bind_data(tmp_path: Path) -> None:
    deployment, environment, _docker_log = _stage_installer(tmp_path)
    data_root = tmp_path / "operator-owned"
    data_root.mkdir()
    state = data_root / "keep.txt"
    state.write_text("keep", encoding="utf-8")
    (deployment / ".env").write_text(
        f"MAINSTAY_DATA_ROOT={data_root}\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [str(deployment / "teardown-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input="DELETE\n",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert state.read_text(encoding="utf-8") == "keep"
    assert "data root was not installer-managed" in result.stdout
