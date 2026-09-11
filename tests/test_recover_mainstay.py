from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]


def _stage_recovery(tmp_path: Path) -> tuple[Path, dict[str, str], Path]:
    deployment = tmp_path / "deployment"
    deployment.mkdir()
    for name in (
        "docker-compose.yaml",
        "recover-mainstay.sh",
        "save-recovery-env.sh",
        "start-mainstay.sh",
        "init-env.sh",
        ".env.example",
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
if [ "$1" = "ps" ]; then exit 0; fi
if [ "$1" = "compose" ]; then exit 0; fi
exit 0
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)
    ss = fake_bin / "ss"
    ss.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
    ss.chmod(0o755)

    environment = os.environ.copy()
    environment["PATH"] = f"{fake_bin}:{environment['PATH']}"
    environment["DOCKER_LOG"] = str(docker_log)
    return deployment, environment, docker_log


def _create_recovered_instance(tmp_path: Path, name: str) -> Path:
    data_root = tmp_path / "data" / name
    for directory in (
        "mainstay-control",
        "safebox-web",
        "spurline",
        "grove",
        "clear",
    ):
        (data_root / directory).mkdir(parents=True, exist_ok=True)
    (data_root / ".env.recovery").write_text(
        """COMPOSE_PROJECT_NAME=old-project
MAINSTAY_INSTANCE_NAME=Original Venue
MAINSTAY_DATA_ROOT=/old/location/old-project
MAINSTAY_LOCAL_BIND_ADDRESS=0.0.0.0
MAINSTAY_LOCAL_PORT=8788
MAINSTAY_SAFEBOX_BIND_ADDRESS=0.0.0.0
MAINSTAY_SAFEBOX_PORT=8888
MAINSTAY_INSTALLATION_NSEC=installation-key
CLEAR_MASTER_SECRET=clear-master
CLEAR_OPERATOR_TOKEN=clear-operator
CLEAR_MINT_SERVICE_NSEC=clear-service-key
SPURLINE_SERVICE_NSEC=spurline-service-key
GROVE_SERVICE_NSEC=grove-service-key
SAFEBOX_WEB_SERVICE_NSEC=safebox-web-service-key
SAFEBOX_COOKIE_KEY=cookie-key
SAFEBOX_ONBOARD_INVITE_CODE=invite-code
""",
        encoding="utf-8",
    )
    return data_root


def _read_env(path: Path) -> dict[str, str]:
    return {
        key: value
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#") and "=" in line
        for key, value in [line.split("=", 1)]
    }


def test_recovery_uses_existing_data_root_name_as_compose_name(
    tmp_path: Path,
) -> None:
    deployment, environment, docker_log = _stage_recovery(tmp_path)
    data_root = _create_recovered_instance(tmp_path, "private-venue")
    answers = f"{data_root}\n1\n" + "\n" * 5 + "no\nyes\n"

    result = subprocess.run(
        [str(deployment / "recover-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input=answers,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    values = _read_env(deployment / ".env")
    assert values["COMPOSE_PROJECT_NAME"] == "private-venue"
    assert values["MAINSTAY_INSTANCE_NAME"] == "Original Venue"
    assert values["MAINSTAY_LOCAL_IMAGE"] == "private-venue-control:local"
    assert values["SAFEBOX_IMAGE"] == "private-venue-safebox-web:local"
    assert values["MAINSTAY_SPURLINE_IMAGE"] == "private-venue-spurline:local"
    assert values["MAINSTAY_GROVE_IMAGE"] == "private-venue-grove:local"
    assert values["MAINSTAY_CLEAR_IMAGE"] == "private-venue-clear:local"
    assert values["MAINSTAY_DATA_PARENT"] == str(data_root.parent)
    assert values["MAINSTAY_DATA_DIRECTORY_NAME"] == "private-venue"
    assert values["MAINSTAY_DATA_ROOT"] == str(data_root)
    assert values["MAINSTAY_LOCAL_DATA_SOURCE"] == str(
        data_root / "mainstay-control"
    )
    assert values["CLEAR_MASTER_SECRET"] == "clear-master"
    assert stat.S_IMODE((deployment / ".env").stat().st_mode) == 0o600
    assert "Recovery preflight passed" in result.stdout
    assert "compose --env-file" in docker_log.read_text(encoding="utf-8")


def test_recovery_allows_a_different_compose_name_after_warning(
    tmp_path: Path,
) -> None:
    deployment, environment, _docker_log = _stage_recovery(tmp_path)
    data_root = _create_recovered_instance(tmp_path, "old-directory")
    answers = (
        f"{data_root}\n2\nnew-runtime\nyes\n"
        + "\n" * 5
        + "no\nyes\n"
    )

    result = subprocess.run(
        [str(deployment / "recover-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input=answers,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    values = _read_env(deployment / ".env")
    assert values["COMPOSE_PROJECT_NAME"] == "new-runtime"
    assert values["SAFEBOX_IMAGE"] == "new-runtime-safebox-web:local"
    assert values["MAINSTAY_DATA_DIRECTORY_NAME"] == "old-directory"
    assert values["MAINSTAY_DATA_ROOT"] == str(data_root)
    assert "Compose project name will differ" in result.stderr
    assert "Compose and data-root names will remain different" in result.stdout


def test_recovery_preserves_custom_image_override(tmp_path: Path) -> None:
    deployment, environment, _docker_log = _stage_recovery(tmp_path)
    data_root = _create_recovered_instance(tmp_path, "custom-images")
    recovery_file = data_root / ".env.recovery"
    recovery_file.write_text(
        recovery_file.read_text(encoding="utf-8")
        + "SAFEBOX_IMAGE=registry.example/safebox-web:stable\n",
        encoding="utf-8",
    )
    answers = f"{data_root}\n1\n" + "\n" * 5 + "no\nyes\n"

    result = subprocess.run(
        [str(deployment / "recover-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input=answers,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    values = _read_env(deployment / ".env")
    assert values["SAFEBOX_IMAGE"] == "registry.example/safebox-web:stable"
    assert values["MAINSTAY_CLEAR_IMAGE"] == "custom-images-clear:local"


def test_recovery_can_abort_before_writing(tmp_path: Path) -> None:
    deployment, environment, _docker_log = _stage_recovery(tmp_path)

    result = subprocess.run(
        [str(deployment / "recover-mainstay.sh")],
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


def test_recovery_refuses_missing_identity_material(tmp_path: Path) -> None:
    deployment, environment, _docker_log = _stage_recovery(tmp_path)
    data_root = _create_recovered_instance(tmp_path, "incomplete")
    recovery_file = data_root / ".env.recovery"
    recovery_file.write_text(
        recovery_file.read_text(encoding="utf-8").replace(
            "CLEAR_MASTER_SECRET=clear-master",
            "CLEAR_MASTER_SECRET=",
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [str(deployment / "recover-mainstay.sh")],
        cwd=deployment,
        env=environment,
        input=f"{data_root}\n",
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "missing required CLEAR_MASTER_SECRET" in result.stderr
    assert not (deployment / ".env").exists()
