from __future__ import annotations

import os
import shutil
import stat
import subprocess
from pathlib import Path

PROJECT_ROOT = Path(__file__).parents[1]
IDENTITY_VALUES = {
    "MAINSTAY_INSTALLATION_NSEC": "installation-key",
    "CLEAR_MASTER_SECRET": "clear-master",
    "CLEAR_MINT_SERVICE_NSEC": "clear-service-key",
    "SPURLINE_SERVICE_NSEC": "spurline-service-key",
    "GROVE_SERVICE_NSEC": "grove-service-key",
    "SAFEBOX_WEB_SERVICE_NSEC": "safebox-web-service-key",
    "SAFEBOX_COOKIE_KEY": "cookie-key",
}


def _write_env(path: Path, data_root: Path, **overrides: str) -> None:
    values = {**IDENTITY_VALUES, **overrides}
    lines = [f"MAINSTAY_DATA_ROOT={data_root}"]
    lines.extend(f"{key}={value}" for key, value in values.items())
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _stage_helper(tmp_path: Path) -> Path:
    script = tmp_path / "save-recovery-env.sh"
    shutil.copy2(PROJECT_ROOT / "save-recovery-env.sh", script)
    return script


def test_save_recovery_env_creates_private_atomic_copy(tmp_path: Path) -> None:
    script = _stage_helper(tmp_path)
    data_root = tmp_path / "instance"
    data_root.mkdir()
    env_file = tmp_path / ".env"
    _write_env(env_file, data_root)

    result = subprocess.run(
        [str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    recovery_file = data_root / ".env.recovery"
    assert result.returncode == 0, result.stderr
    assert recovery_file.read_text(encoding="utf-8") == env_file.read_text(
        encoding="utf-8"
    )
    assert stat.S_IMODE(recovery_file.stat().st_mode) == 0o600


def test_save_recovery_env_refuses_identity_mismatch(tmp_path: Path) -> None:
    script = _stage_helper(tmp_path)
    data_root = tmp_path / "instance"
    data_root.mkdir()
    env_file = tmp_path / ".env"
    _write_env(env_file, data_root)
    subprocess.run([str(script)], cwd=tmp_path, check=True)
    original = (data_root / ".env.recovery").read_text(encoding="utf-8")
    _write_env(env_file, data_root, CLEAR_MASTER_SECRET="different-master")

    result = subprocess.run(
        [str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
    )

    assert result.returncode == 1
    assert "CLEAR_MASTER_SECRET does not match" in result.stderr
    assert (data_root / ".env.recovery").read_text(encoding="utf-8") == original


def test_save_recovery_env_skips_docker_managed_storage(tmp_path: Path) -> None:
    script = _stage_helper(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text("MAINSTAY_DATA_ROOT=\n", encoding="utf-8")

    result = subprocess.run(
        [str(script)],
        cwd=tmp_path,
        capture_output=True,
        text=True,
        check=False,
        env=os.environ.copy(),
    )

    assert result.returncode == 0
    assert result.stdout == ""
