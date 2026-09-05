from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

from .env import render_safebox_env
from .registry import BundleConfig
from .server import serve
from .status import check_bundle

DEFAULT_CONFIG_PATH = Path(
    os.getenv("MAINSTAY_LOCAL_CONFIG", "mainstay-local.json")
)
DEFAULT_ENV_PATH = Path("build/mainstay-local/safebox-web.env")
DEFAULT_COMPOSE_PATH = Path("docker-compose.yaml")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="mainstay-local",
        description="Local-first Mainstay control-plane prototype.",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init", help="Create a starter registry.")
    _add_config_argument(init_parser)
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Replace an existing registry file.",
    )

    config_parser = subparsers.add_parser(
        "config",
        help="Render Safebox Web environment settings from the registry.",
    )
    _add_config_argument(config_parser)
    config_parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_ENV_PATH,
        help="Environment file to write.",
    )

    status_parser = subparsers.add_parser("status", help="Check service health.")
    _add_config_argument(status_parser)
    status_parser.add_argument(
        "--timeout",
        type=float,
        default=2.0,
        help="HTTP timeout in seconds for each health check.",
    )

    up_parser = subparsers.add_parser("up", help="Start the local Docker bundle.")
    _add_config_argument(up_parser)
    up_parser.add_argument(
        "--compose-file",
        type=Path,
        default=DEFAULT_COMPOSE_PATH,
        help="Compose file to run.",
    )
    up_parser.add_argument(
        "--env-file",
        type=Path,
        default=DEFAULT_ENV_PATH,
        help="Environment file to pass to Docker Compose.",
    )
    up_parser.add_argument(
        "--detach",
        action="store_true",
        help="Start in detached mode.",
    )

    serve_parser = subparsers.add_parser(
        "serve",
        help="Run the local control-plane HTTP surface.",
    )
    _add_config_argument(serve_parser)
    serve_parser.add_argument(
        "--host",
        default=os.getenv("MAINSTAY_LOCAL_HOST"),
        help="Host address to bind.",
    )
    serve_parser.add_argument(
        "--port",
        type=int,
        default=_env_int("MAINSTAY_LOCAL_PORT"),
        help="Port to bind.",
    )

    args = parser.parse_args(argv)

    if args.command == "init":
        return _init(args.config, force=args.force)
    if args.command == "config":
        return _config(args.config, args.output)
    if args.command == "status":
        return _status(args.config, timeout=args.timeout)
    if args.command == "up":
        return _up(args.config, args.compose_file, args.env_file, args.detach)
    if args.command == "serve":
        return _serve(args.config, host=args.host, port=args.port)

    parser.error(f"unknown command: {args.command}")
    return 2


def _add_config_argument(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help="Path to the mainstay-local registry JSON file.",
    )


def _env_int(name: str) -> int | None:
    value = os.getenv(name)
    if not value:
        return None
    return int(value)


def _init(config_path: Path, *, force: bool) -> int:
    if config_path.exists() and not force:
        print(
            f"{config_path} already exists. Use --force to replace it.",
            file=sys.stderr,
        )
        return 1
    config_path.parent.mkdir(parents=True, exist_ok=True)
    config_path.write_text(BundleConfig.default().to_json(), encoding="utf-8")
    print(f"Wrote {config_path}")
    return 0


def _config(config_path: Path, output_path: Path) -> int:
    bundle = BundleConfig.from_json(config_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(render_safebox_env(bundle), encoding="utf-8")
    print(f"Wrote {output_path}")
    return 0


def _status(config_path: Path, *, timeout: float) -> int:
    bundle = BundleConfig.from_json(config_path)
    results = check_bundle(bundle, timeout=timeout)
    width = max(len(result.name) for result in results) if results else 0
    failed = False
    for result in results:
        state = "ok" if result.ok else "fail"
        print(f"{result.name.ljust(width)}  {state}  {result.target}")
        if result.detail:
            print(f"{' ' * width}        {result.detail}")
        failed = failed or not result.ok
    return 1 if failed else 0


def _up(
    config_path: Path,
    compose_path: Path,
    env_path: Path,
    detach: bool,
) -> int:
    BundleConfig.from_json(config_path)
    _config(config_path, env_path)
    command = [
        "docker",
        "compose",
        "--env-file",
        str(env_path),
        "-f",
        str(compose_path),
    ]
    command.extend(["up", "--build"])
    if detach:
        command.append("--detach")
    return subprocess.call(command)


def _serve(config_path: Path, *, host: str | None, port: int | None) -> int:
    bundle = (
        BundleConfig.from_json(config_path)
        if config_path.exists()
        else BundleConfig.default()
    )
    serve(bundle, host=host or bundle.host, port=port or bundle.port)
    return 0
