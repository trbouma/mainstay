from __future__ import annotations

import json
import sqlite3
import subprocess
import unittest
from pathlib import Path
from unittest.mock import patch

from app.clear_context import (
    LocalClearError,
    LocalClearRecipient,
    RegisteredHandle,
    clear_info,
    list_clear_cmus,
    list_registered_handles,
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

    def read(self, size: int = -1) -> bytes:
        return self.body if size < 0 else self.body[:size]


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

    def test_lists_registered_handles_from_safebox_database(self) -> None:
        path = Path(self._testMethodName).with_suffix(".db")
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        with sqlite3.connect(path) as connection:
            connection.execute(
                """
                CREATE TABLE claimed_handle (
                    id INTEGER PRIMARY KEY,
                    claimed_handle TEXT NOT NULL,
                    npub TEXT NOT NULL,
                    home_relay TEXT NOT NULL
                )
                """
            )
            connection.execute(
                """
                INSERT INTO claimed_handle
                (claimed_handle, npub, home_relay)
                VALUES (?, ?, ?)
                """,
                (
                    "alice",
                    "npub14w46h2at4w46h2at4w46h2at4w46h2at4w46h2at4w46h2at4w4scf6zts",
                    "ws://spurline:8080",
                ),
            )

        self.assertEqual(
            list_registered_handles(database_path=path),
            [
                RegisteredHandle(
                    handle="alice",
                    pubkey=PUBKEY,
                    npub="npub14w46h2at4w46h2at4w46h2at4w46h2at4w46h2at4w46h2at4w4scf6zts",
                    relays=("ws://spurline:8080",),
                )
            ],
        )

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

    def test_send_prefers_clear_operator_api_when_token_is_available(self) -> None:
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
            patch.dict(
                "os.environ",
                {
                    "CLEAR_OPERATOR_TOKEN": "operator-token",
                    "CLEAR_OPERATOR_API_URL": "http://clear-operator:3340",
                },
            ),
            patch(
                "app.clear_context.resolve_local_clear_recipient",
                return_value=LocalClearRecipient("alice", PUBKEY),
            ),
            patch(
                "app.clear_context.urlopen",
                return_value=FakeResponse(root_result),
            ) as urlopen,
            patch("app.clear_context.subprocess.run") as run,
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

        request = urlopen.call_args.args[0]
        self.assertEqual(
            request.full_url,
            "http://clear-operator:3340/v1/operator/root/send",
        )
        self.assertEqual(request.headers["Authorization"], "Bearer operator-token")
        self.assertEqual(json.loads(request.data), {
            "amount": 20,
            "address": PUBKEY,
            "memo": "hello",
            "relays": ["ws://spurline:8080"],
            "allow_internal_mint_delivery": True,
        })
        run.assert_not_called()
        self.assertEqual(receipt["amount"], 20)
        self.assertNotIn("cashu-secret", json.dumps(receipt))
        self.assertNotIn("proof-secret", json.dumps(receipt))

    def test_clear_info_reads_public_info_and_operator_summary(self) -> None:
        calls = []

        def open_response(request, *, timeout):
            calls.append((request.full_url, request.headers.get("Authorization")))
            if request.full_url.endswith("/v1/info"):
                return FakeResponse(
                    {
                        "currency": {"unit": "cmu-root"},
                        "service_identity": {"npub": "npub1clear"},
                    }
                )
            return FakeResponse(
                {"unit": "cmu-root", "issued": 120, "outstanding": 80}
            )

        with (
            patch.dict("os.environ", {"CLEAR_OPERATOR_TOKEN": "operator-token"}),
            patch("app.clear_context.urlopen", side_effect=open_response),
        ):
            result = clear_info(BundleConfig.default(), timeout=2)

        self.assertEqual(result["status"], "OK")
        self.assertEqual(result["info"]["currency"]["unit"], "cmu-root")
        self.assertEqual(result["root_summary"]["outstanding"], 80)
        self.assertEqual(
            calls,
            [
                ("http://clear:3339/v1/info", None),
                (
                    "http://clear:3339/v1/operator/summary",
                    "Bearer operator-token",
                ),
            ],
        )

    def test_clear_cmu_list_marks_instance_owned_cmu(self) -> None:
        calls = []

        def open_response(request, *, timeout):
            calls.append((request.full_url, request.headers.get("Authorization")))
            if request.full_url.endswith("/v1/info"):
                return FakeResponse({"currency": {"unit": "cmu-root"}})
            return FakeResponse(
                {
                    "cmus": [
                        {"unit": "cmu-root", "status": "active"},
                        {"unit": "cmu-treasurer", "status": "active"},
                    ]
                }
            )

        with (
            patch.dict("os.environ", {"CLEAR_OPERATOR_TOKEN": "operator-token"}),
            patch("app.clear_context.urlopen", side_effect=open_response),
        ):
            result = list_clear_cmus(BundleConfig.default(), timeout=2)

        self.assertEqual(result["instance_cmu"], "cmu-root")
        self.assertTrue(result["cmus"][0]["instance_owned"])
        self.assertFalse(result["cmus"][1]["instance_owned"])
        self.assertEqual(
            calls,
            [
                ("http://clear:3339/v1/info", None),
                (
                    "http://clear:3339/v1/operator/cmus",
                    "Bearer operator-token",
                ),
            ],
        )

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

    def test_cli_exposes_clear_info(self) -> None:
        payload = {"status": "OK", "info": {"currency": {"unit": "cmu-root"}}}
        with (
            patch("app.cli.clear_info", return_value=payload) as info,
            patch("builtins.print") as output,
        ):
            result = main(["clear", "info", "--timeout", "5"])

        self.assertEqual(result, 0)
        self.assertEqual(info.call_args.kwargs["timeout"], 5)
        output.assert_called_once_with(json.dumps(payload, indent=2))

    def test_cli_exposes_clear_cmu_list(self) -> None:
        payload = {
            "status": "OK",
            "instance_cmu": "cmu-root",
            "cmus": [{"unit": "cmu-root", "instance_owned": True}],
        }
        with (
            patch("app.cli.list_clear_cmus", return_value=payload) as cmus,
            patch("builtins.print") as output,
        ):
            result = main(["clear", "cmu", "list", "--timeout", "5"])

        self.assertEqual(result, 0)
        self.assertEqual(cmus.call_args.kwargs["timeout"], 5)
        output.assert_called_once_with(json.dumps(payload, indent=2))

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

    def test_cli_lists_registered_handles(self) -> None:
        handles = [
            RegisteredHandle(
                handle="alice",
                pubkey=PUBKEY,
                npub="npub1alice",
                relays=("ws://spurline:8080",),
            )
        ]
        with (
            patch(
                "app.cli.list_registered_handles",
                return_value=handles,
            ) as list_handles,
            patch("builtins.print") as output,
        ):
            result = main(["handles", "--database", "/tmp/safebox.db", "--json"])

        self.assertEqual(result, 0)
        list_handles.assert_called_once_with(database_path=Path("/tmp/safebox.db"))
        output.assert_called_once_with(
            json.dumps(
                {
                    "handles": [
                        {
                            "handle": "alice",
                            "npub": "npub1alice",
                            "pubkey": PUBKEY,
                            "home_relays": ["ws://spurline:8080"],
                        }
                    ]
                },
                indent=2,
            )
        )


if __name__ == "__main__":
    unittest.main()
