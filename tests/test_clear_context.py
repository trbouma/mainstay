from __future__ import annotations

import json
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from app.clear_context import (
    LocalClearError,
    LocalClearRecipient,
    resolve_local_clear_recipient,
    send_local_clear,
)
from app.cli import main
from app.registry import BundleConfig

PUBKEY = "ab" * 32


class FakeResponse:
    status = 200

    def __init__(self, payload: dict[str, object]) -> None:
        self.body = json.dumps(payload).encode()

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None

    def read(self, size: int) -> bytes:
        return self.body[:size]


def directory_payload() -> dict[str, object]:
    return {
        "names": {"alice": PUBKEY},
        "clear": {
            "alice": {
                "protocols": ["clear-token-transfer"],
                "transports": ["nip59"],
                "kinds": [7379],
            }
        },
    }


class LocalClearContextTests(unittest.TestCase):
    def test_resolves_recipient_through_local_safebox_directory(self) -> None:
        with patch(
            "app.clear_context.urlopen",
            return_value=FakeResponse(directory_payload()),
        ) as urlopen:
            recipient = resolve_local_clear_recipient(
                BundleConfig.default(),
                "Alice",
                timeout=3,
            )

        self.assertEqual(recipient, LocalClearRecipient("alice", PUBKEY))
        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "http://127.0.0.1:8888/.well-known/nostr.json?name=alice",
        )
        self.assertEqual(urlopen.call_args.kwargs["timeout"], 3)

    def test_rejects_full_nip05_address_without_network_lookup(self) -> None:
        with (
            patch("app.clear_context.urlopen") as urlopen,
            self.assertRaisesRegex(LocalClearError, "bare handle"),
        ):
            resolve_local_clear_recipient(
                BundleConfig.default(),
                "alice@example.test",
                timeout=2,
            )

        urlopen.assert_not_called()

    def test_rejects_handle_without_clear_receive_capability(self) -> None:
        payload = directory_payload()
        payload["clear"] = {}
        with (
            patch(
                "app.clear_context.urlopen",
                return_value=FakeResponse(payload),
            ),
            self.assertRaisesRegex(LocalClearError, "Clear support"),
        ):
            resolve_local_clear_recipient(
                BundleConfig.default(),
                "alice",
                timeout=2,
            )

    def test_send_uses_managed_context_and_redacts_bearer_value(self) -> None:
        root_result = {
            "amount": 20,
            "unit": "cmu-test",
            "mint": "http://clear:3339",
            "token": "cashu-secret",
            "proofs": [{"secret": "proof-secret"}],
            "delivery": {"recipient_npub": "npub1alice"},
            "publish": {
                "status": "OK",
                "event_id": "event-id",
                "relays": ["ws://spurline:8080"],
                "verified_relays": ["ws://spurline:8080"],
                "verified": True,
            },
        }
        with (
            patch(
                "app.clear_context.resolve_local_clear_recipient",
                return_value=LocalClearRecipient("alice", PUBKEY),
            ),
            patch(
                "app.clear_context.subprocess.run",
                return_value=subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout=json.dumps(root_result),
                    stderr="",
                ),
            ) as run,
        ):
            receipt = send_local_clear(
                BundleConfig.default(),
                amount=20,
                handle="alice",
                memo="hello",
                compose_path=Path("docker-compose.yaml"),
                env_path=Path(".env"),
                timeout=2,
            )

        self.assertEqual(
            run.call_args.args[0],
            [
                "docker",
                "compose",
                "--env-file",
                ".env",
                "-f",
                "docker-compose.yaml",
                "exec",
                "-T",
                "clear",
                "clear-root",
                "send",
                "20",
                PUBKEY,
                "--allow-internal-mint-delivery",
                "--relay",
                "ws://spurline:8080",
                "--memo",
                "hello",
            ],
        )
        self.assertEqual(receipt["amount"], 20)
        self.assertEqual(receipt["recipient"]["handle"], "alice")
        self.assertNotIn("cashu-secret", json.dumps(receipt))
        self.assertNotIn("proof-secret", json.dumps(receipt))

    def test_unreadable_success_requires_reconciliation(self) -> None:
        with (
            patch(
                "app.clear_context.resolve_local_clear_recipient",
                return_value=LocalClearRecipient("alice", PUBKEY),
            ),
            patch(
                "app.clear_context.subprocess.run",
                return_value=subprocess.CompletedProcess(
                    args=[],
                    returncode=0,
                    stdout="not-json",
                    stderr="",
                ),
            ),
            self.assertRaisesRegex(LocalClearError, "do not retry"),
        ):
            send_local_clear(
                BundleConfig.default(),
                amount=20,
                handle="alice",
                memo=None,
                compose_path=Path("docker-compose.yaml"),
                env_path=None,
                timeout=2,
            )

    def test_cli_exposes_clear_send(self) -> None:
        receipt = {"status": "OK", "amount": 20}
        with (
            patch("app.cli.send_local_clear", return_value=receipt) as send,
            patch("builtins.print") as output,
        ):
            result = main(
                [
                    "clear",
                    "send",
                    "20",
                    "alice",
                    "--memo",
                    "hello",
                    "--env-file",
                    ".env",
                ]
            )

        self.assertEqual(result, 0)
        self.assertEqual(send.call_args.kwargs["amount"], 20)
        self.assertEqual(send.call_args.kwargs["handle"], "alice")
        self.assertEqual(send.call_args.kwargs["memo"], "hello")
        self.assertEqual(send.call_args.kwargs["env_path"], Path(".env"))
        output.assert_called_once_with(json.dumps(receipt, indent=2))

    def test_cli_can_load_a_custom_deployment_registry(self) -> None:
        bundle = BundleConfig.default()
        with (
            patch("app.cli.BundleConfig.from_json", return_value=bundle) as load,
            patch("app.cli.send_local_clear", return_value={"status": "OK"}),
            patch("builtins.print"),
        ):
            result = main(
                [
                    "clear",
                    "send",
                    "20",
                    "alice",
                    "--config",
                    "venue.json",
                ]
            )

        self.assertEqual(result, 0)
        load.assert_called_once_with(Path("venue.json"))


if __name__ == "__main__":
    unittest.main()
