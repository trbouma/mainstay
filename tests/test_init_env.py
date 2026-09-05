from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]


def _stage_helper(tmp_path: Path) -> tuple[Path, dict[str, str]]:
    script = tmp_path / "init-env.sh"
    shutil.copy2(PROJECT_ROOT / "init-env.sh", script)
    shutil.copy2(PROJECT_ROOT / ".env.example", tmp_path / ".env.example")

    bin_dir = tmp_path / "bin"
    bin_dir.mkdir()
    docker = bin_dir / "docker"
    docker.write_text(
        """#!/bin/sh
if [ "$1" = "info" ]; then
    exit 0
fi
if [ "$1" = "volume" ] && [ "$2" = "inspect" ]; then
    if [ "$3" = "mainstay-local_clear-data" ] && \
        [ "${MOCK_CLEAR_VOLUME_EXISTS:-0}" = "1" ]; then
        exit 0
    fi
    if [ "$3" = "mainstay-local_safebox-web-data" ] && \
        [ "${MOCK_SAFEBOX_VOLUME_EXISTS:-0}" = "1" ]; then
        exit 0
    fi
fi
exit 1
""",
        encoding="utf-8",
    )
    docker.chmod(0o755)

    environment = os.environ.copy()
    environment["PATH"] = f"{bin_dir}:{environment['PATH']}"
    return script, environment


def _read_env(path: Path) -> dict[str, str]:
    return {
        key: value
        for line in path.read_text(encoding="utf-8").splitlines()
        if line and not line.startswith("#") and "=" in line
        for key, value in [line.split("=", 1)]
    }


def test_init_env_creates_private_file_with_independent_secrets(tmp_path: Path) -> None:
    script, environment = _stage_helper(tmp_path)

    result = subprocess.run(
        [str(script)],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )

    env_file = tmp_path / ".env"
    values = _read_env(env_file)
    assert result.stdout == "Created .env with generated Mainstay secrets.\n"
    assert len(values["CLEAR_MASTER_SECRET"]) == 64
    assert len(values["CLEAR_OPERATOR_TOKEN"]) == 64
    assert len(values["SAFEBOX_COOKIE_KEY"]) == 44
    assert values["SAFEBOX_COOKIE_KEY"].endswith("=")
    assert len(values["SAFEBOX_ONBOARD_INVITE_CODE"]) == 32
    assert values["CLEAR_MASTER_SECRET"] != values["CLEAR_OPERATOR_TOKEN"]
    assert stat.S_IMODE(env_file.stat().st_mode) == 0o600
    assert values["CLEAR_MASTER_SECRET"] not in result.stdout
    assert values["CLEAR_OPERATOR_TOKEN"] not in result.stdout
    assert values["SAFEBOX_COOKIE_KEY"] not in result.stdout
    assert values["SAFEBOX_ONBOARD_INVITE_CODE"] not in result.stdout


def test_init_env_refuses_new_identity_for_existing_volume(tmp_path: Path) -> None:
    script, environment = _stage_helper(tmp_path)
    environment["MOCK_CLEAR_VOLUME_EXISTS"] = "1"

    result = subprocess.run(
        [str(script)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.returncode == 1
    assert not (tmp_path / ".env").exists()
    assert "Refusing to generate CLEAR_MASTER_SECRET" in result.stderr


def test_init_env_refuses_new_cookie_key_for_existing_safebox_volume(
    tmp_path: Path,
) -> None:
    script, environment = _stage_helper(tmp_path)
    environment["MOCK_SAFEBOX_VOLUME_EXISTS"] = "1"
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CLEAR_MASTER_SECRET=existing-master\n"
        "CLEAR_OPERATOR_TOKEN=existing-operator\n"
        "SAFEBOX_COOKIE_KEY=\n"
        "SAFEBOX_ONBOARD_INVITE_CODE=existing-invite\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [str(script)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.returncode == 1
    assert "Refusing to generate SAFEBOX_COOKIE_KEY" in result.stderr
    assert _read_env(env_file)["SAFEBOX_COOKIE_KEY"] == ""


def test_init_env_fills_missing_secrets_in_existing_file(tmp_path: Path) -> None:
    script, environment = _stage_helper(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "MAINSTAY_LOCAL_PORT=9876\n"
        "CLEAR_MASTER_SECRET=\n"
        "CLEAR_OPERATOR_TOKEN=\n"
        "SAFEBOX_COOKIE_KEY=\n"
        "SAFEBOX_ONBOARD_INVITE_CODE=\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [str(script)],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )

    values = _read_env(env_file)
    assert result.stdout == "Added missing Mainstay secrets to .env.\n"
    assert values["MAINSTAY_LOCAL_PORT"] == "9876"
    assert len(values["CLEAR_MASTER_SECRET"]) == 64
    assert len(values["CLEAR_OPERATOR_TOKEN"]) == 64
    assert len(values["SAFEBOX_COOKIE_KEY"]) == 44
    assert len(values["SAFEBOX_ONBOARD_INVITE_CODE"]) == 32
    assert stat.S_IMODE(env_file.stat().st_mode) == 0o600


def test_init_env_is_idempotent(tmp_path: Path) -> None:
    script, environment = _stage_helper(tmp_path)
    subprocess.run([str(script)], check=True, env=environment)
    env_file = tmp_path / ".env"
    original = env_file.read_text(encoding="utf-8")

    result = subprocess.run(
        [str(script)],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.stdout == ".env already contains the required Mainstay secrets.\n"
    assert env_file.read_text(encoding="utf-8") == original
