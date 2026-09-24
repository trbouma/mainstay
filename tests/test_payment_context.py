import json
from unittest.mock import patch

import pytest

from app.cli import main


class Response:
    def __enter__(self):
        return self

    def __exit__(self, *args):
        pass

    def read(self):
        return b'{"dry_run": true}'


@pytest.fixture(autouse=True)
def management(monkeypatch):
    monkeypatch.setenv("MAINSTAY_SAFEBOX_MANAGEMENT_URL", "http://safebox-web:8000")
    monkeypatch.setenv("SAFEBOX_MANAGEMENT_TOKEN", "test-token")


@pytest.mark.parametrize("confirmed", [False, True])
def test_close_is_preview_unless_explicitly_confirmed(confirmed):
    args = ["payments", "close", "abc123", "--handle", "trbouma", "--amount", "111",
            "--operator", "tester", "--reason", "Abandoned test payment"]
    if confirmed:
        args.append("--yes")
    with patch("app.payment_context.urlopen", return_value=Response()) as call:
        assert main(args) == 0
    request = call.call_args.args[0]
    assert request.full_url == "http://safebox-web:8000/internal/provider-payments/abc123/close"
    assert request.get_header("Authorization") == "Bearer test-token"
    payload = json.loads(request.data)
    assert payload["confirmed"] is confirmed
    assert payload["amount_sat"] == 111
    assert payload["operator"] == "tester"


@pytest.mark.parametrize("args,path", [
    (["payments", "list", "--handle", "trbouma"],
     "/internal/provider-payments?handle=trbouma"),
    (["payments", "show", "abc123"], "/internal/provider-payments/abc123"),
])
def test_inspection_is_read_only(args, path):
    with patch("app.payment_context.urlopen", return_value=Response()) as call:
        assert main(args) == 0
    request = call.call_args.args[0]
    assert request.full_url.endswith(path)
    assert request.get_method() == "GET"


def test_missing_management_credentials_fails_closed(monkeypatch, capsys):
    monkeypatch.delenv("SAFEBOX_MANAGEMENT_TOKEN")
    with patch("app.payment_context.urlopen") as call:
        assert main(["payments", "show", "abc123"]) == 1
    call.assert_not_called()
    assert "SAFEBOX_MANAGEMENT_TOKEN" in capsys.readouterr().err


def test_missing_reason_is_rejected():
    with pytest.raises(SystemExit):
        main(["payments", "close", "abc123", "--handle", "trbouma", "--amount",
              "111", "--operator", "tester", "--yes"])
