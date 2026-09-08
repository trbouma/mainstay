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
    if [ "$3" = "${MOCK_CLEAR_VOLUME_NAME:-mainstay-local_clear-data}" ] && \
        [ "${MOCK_CLEAR_VOLUME_EXISTS:-0}" = "1" ]; then
        exit 0
    fi
    if [ "$3" = "${MOCK_SAFEBOX_VOLUME_NAME:-mainstay-local_safebox-web-data}" ] && \
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
    assert result.stdout.startswith("Created .env with generated Mainstay secrets.\n")
    assert "operator-funded service-Acorn fee reserve" in result.stdout
    assert "app.service_acorn_worker fund 100" in result.stdout
    assert len(values["CLEAR_MASTER_SECRET"]) == 64
    assert len(values["CLEAR_OPERATOR_TOKEN"]) == 64
    assert len(values["CLEAR_MINT_SERVICE_NSEC"]) == 64
    assert len(values["SPURLINE_SERVICE_NSEC"]) == 64
    assert len(values["GROVE_SERVICE_NSEC"]) == 64
    assert len(values["MAINSTAY_INSTALLATION_NSEC"]) == 64
    assert len(values["SAFEBOX_COOKIE_KEY"]) == 44
    assert values["SAFEBOX_COOKIE_KEY"].endswith("=")
    assert len(values["SAFEBOX_ONBOARD_INVITE_CODE"]) == 32
    assert values["CLEAR_MASTER_SECRET"] != values["CLEAR_OPERATOR_TOKEN"]
    assert values["CLEAR_MINT_SERVICE_NSEC"] not in {
        values["CLEAR_MASTER_SECRET"],
        values["CLEAR_OPERATOR_TOKEN"],
        values["SPURLINE_SERVICE_NSEC"],
        values["GROVE_SERVICE_NSEC"],
        values["MAINSTAY_INSTALLATION_NSEC"],
    }
    assert stat.S_IMODE(env_file.stat().st_mode) == 0o600
    assert values["CLEAR_MASTER_SECRET"] not in result.stdout
    assert values["CLEAR_OPERATOR_TOKEN"] not in result.stdout
    assert values["CLEAR_MINT_SERVICE_NSEC"] not in result.stdout
    assert values["SPURLINE_SERVICE_NSEC"] not in result.stdout
    assert values["GROVE_SERVICE_NSEC"] not in result.stdout
    assert values["MAINSTAY_INSTALLATION_NSEC"] not in result.stdout
    assert values["SAFEBOX_COOKIE_KEY"] not in result.stdout
    assert values["SAFEBOX_ONBOARD_INVITE_CODE"] not in result.stdout


def test_init_env_configures_bind_storage_on_first_initialization(
    tmp_path: Path,
) -> None:
    script, environment = _stage_helper(tmp_path)
    data_root = tmp_path / "managed-data"

    subprocess.run(
        [str(script), "--data-root", str(data_root)],
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    )

    values = _read_env(tmp_path / ".env")
    assert values["MAINSTAY_DATA_ROOT"] == str(data_root)
    assert values["MAINSTAY_DATA_RUNTIME_USER"] == f"{os.getuid()}:{os.getgid()}"
    assert values["MAINSTAY_LOCAL_DATA_SOURCE"] == str(data_root / "mainstay-local")
    assert values["MAINSTAY_SAFEBOX_DATA_SOURCE"] == str(data_root / "safebox-web")
    assert values["MAINSTAY_SPURLINE_DATA_SOURCE"] == str(data_root / "spurline")
    assert values["MAINSTAY_GROVE_DATA_SOURCE"] == str(data_root / "grove")
    assert values["MAINSTAY_CLEAR_DATA_SOURCE"] == str(data_root / "clear")
    for directory in (
        "mainstay-local",
        "safebox-web",
        "spurline",
        "grove",
        "clear",
    ):
        assert (data_root / directory).is_dir()


def test_init_env_refuses_to_change_configured_data_root(tmp_path: Path) -> None:
    script, environment = _stage_helper(tmp_path)
    first_root = tmp_path / "first"
    subprocess.run(
        [str(script), "--data-root", str(first_root)],
        check=True,
        env=environment,
    )

    result = subprocess.run(
        [str(script), "--data-root", str(tmp_path / "second")],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.returncode == 1
    assert "Refusing to change MAINSTAY_DATA_ROOT" in result.stderr
    assert _read_env(tmp_path / ".env")["MAINSTAY_DATA_ROOT"] == str(first_root)


def test_init_env_protects_existing_bind_mounted_clear_data(tmp_path: Path) -> None:
    script, environment = _stage_helper(tmp_path)
    data_root = tmp_path / "managed-data"
    clear_data = data_root / "clear"
    clear_data.mkdir(parents=True)
    (clear_data / "clear.sqlite3").write_text("existing", encoding="utf-8")

    result = subprocess.run(
        [str(script), "--data-root", str(data_root)],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )

    assert result.returncode == 1
    assert "because Clear data exists" in result.stderr
    assert not (tmp_path / ".env").exists()


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


def test_init_env_checks_volumes_in_configured_compose_project(
    tmp_path: Path,
) -> None:
    script, environment = _stage_helper(tmp_path)
    environment["MOCK_CLEAR_VOLUME_EXISTS"] = "1"
    environment["MOCK_CLEAR_VOLUME_NAME"] = "mainstay-testlab_clear-data"
    (tmp_path / ".env").write_text(
        "COMPOSE_PROJECT_NAME=mainstay-testlab\n"
        "CLEAR_MASTER_SECRET=\n",
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
        "CLEAR_MINT_SERVICE_NSEC=existing-service-key\n"
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
        "CLEAR_MINT_SERVICE_NSEC=\n"
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
    assert result.stdout.startswith("Added missing Mainstay secrets to .env.\n")
    assert "operator-funded service-Acorn fee reserve" in result.stdout
    assert values["MAINSTAY_LOCAL_PORT"] == "9876"
    assert len(values["CLEAR_MASTER_SECRET"]) == 64
    assert len(values["CLEAR_OPERATOR_TOKEN"]) == 64
    assert len(values["CLEAR_MINT_SERVICE_NSEC"]) == 64
    assert len(values["SPURLINE_SERVICE_NSEC"]) == 64
    assert len(values["GROVE_SERVICE_NSEC"]) == 64
    assert len(values["MAINSTAY_INSTALLATION_NSEC"]) == 64
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

    assert result.stdout.startswith(
        ".env already contains the required Mainstay secrets.\n"
    )
    assert "operator-funded service-Acorn fee reserve" in result.stdout
    assert env_file.read_text(encoding="utf-8") == original


def test_init_env_assigns_first_service_identity_to_existing_clear_volume(
    tmp_path: Path,
) -> None:
    script, environment = _stage_helper(tmp_path)
    environment["MOCK_CLEAR_VOLUME_EXISTS"] = "1"
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CLEAR_MASTER_SECRET=existing-master\n"
        "CLEAR_OPERATOR_TOKEN=existing-operator\n"
        "SAFEBOX_COOKIE_KEY=existing-cookie\n"
        "SAFEBOX_ONBOARD_INVITE_CODE=existing-invite\n",
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
    assert len(values["CLEAR_MINT_SERVICE_NSEC"]) == 64
    assert len(values["SPURLINE_SERVICE_NSEC"]) == 64
    assert len(values["GROVE_SERVICE_NSEC"]) == 64
    assert len(values["MAINSTAY_INSTALLATION_NSEC"]) == 64
    assert values["CLEAR_MINT_SERVICE_NSEC"] not in result.stdout
    assert values["SPURLINE_SERVICE_NSEC"] not in result.stdout
    assert values["GROVE_SERVICE_NSEC"] not in result.stdout


def test_init_env_refuses_to_replace_recorded_installation_identity(
    tmp_path: Path,
) -> None:
    script, environment = _stage_helper(tmp_path)
    state = tmp_path / "build/mainstay-local/installation-identity.json"
    state.parent.mkdir(parents=True)
    state.write_text('{"npub":"npub1existing"}\n', encoding="utf-8")
    env_file = tmp_path / ".env"
    env_file.write_text(
        "CLEAR_MASTER_SECRET=existing-master\n"
        "CLEAR_OPERATOR_TOKEN=existing-operator\n"
        "CLEAR_MINT_SERVICE_NSEC=existing-service-key\n"
        "MAINSTAY_INSTALLATION_NSEC=\n"
        "SAFEBOX_COOKIE_KEY=existing-cookie\n"
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
    assert "Refusing to replace the Mainstay installation identity" in result.stderr
    assert _read_env(env_file)["MAINSTAY_INSTALLATION_NSEC"] == ""
