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
if [ "$1" = "volume" ] && [ "${MOCK_CLEAR_VOLUME_EXISTS:-0}" = "1" ]; then
    exit 0
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
    assert result.stdout == "Created .env with generated Clear secrets.\n"
    assert len(values["CLEAR_MASTER_SECRET"]) == 64
    assert len(values["CLEAR_OPERATOR_TOKEN"]) == 64
    assert values["CLEAR_MASTER_SECRET"] != values["CLEAR_OPERATOR_TOKEN"]
    assert stat.S_IMODE(env_file.stat().st_mode) == 0o600
    assert values["CLEAR_MASTER_SECRET"] not in result.stdout
    assert values["CLEAR_OPERATOR_TOKEN"] not in result.stdout


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


def test_init_env_fills_missing_secrets_in_existing_file(tmp_path: Path) -> None:
    script, environment = _stage_helper(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "MAINSTAY_LOCAL_PORT=9876\n"
        "CLEAR_MASTER_SECRET=\n"
        "CLEAR_OPERATOR_TOKEN=\n",
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
    assert result.stdout == "Added missing Clear secrets to .env.\n"
    assert values["MAINSTAY_LOCAL_PORT"] == "9876"
    assert len(values["CLEAR_MASTER_SECRET"]) == 64
    assert len(values["CLEAR_OPERATOR_TOKEN"]) == 64
    assert stat.S_IMODE(env_file.stat().st_mode) == 0o600
