from __future__ import annotations

import json
import unittest
from unittest.mock import patch
from urllib.request import Request

from app.registry import EndpointAddress, ServiceEndpoint
from app.status import MAX_HOMEPAGE_BYTES, check_service, inspect_homepage


class FakeResponse:
    def __init__(
        self,
        body: bytes = b"",
        *,
        status: int = 200,
        content_type: str = "application/json",
    ) -> None:
        self.body = body
        self.status = status
        self.headers = {"Content-Type": content_type}

    def read(self, amount: int = -1) -> bytes:
        return self.body if amount < 0 else self.body[:amount]

    def __enter__(self) -> FakeResponse:
        return self

    def __exit__(self, *args: object) -> None:
        return None


class ServiceStatusTests(unittest.TestCase):
    def test_healthy_service_includes_json_homepage_report(self) -> None:
        service = ServiceEndpoint(
            name="clear",
            kind="clear-mint",
            endpoints=(
                EndpointAddress("internal", "mint", "http://clear:3339"),
            ),
            health_url="http://clear:3339/health",
            homepage_url="http://clear:3339/",
        )
        homepage = json.dumps(
            {"name": "Clear", "currency": {"name": "Mainstay Local Credits"}}
        ).encode()

        def open_response(target: str | Request, *, timeout: float) -> FakeResponse:
            self.assertEqual(timeout, 1.0)
            if isinstance(target, Request):
                self.assertEqual(target.full_url, service.homepage_url)
                self.assertIn("application/json", target.get_header("Accept"))
                return FakeResponse(homepage)
            self.assertEqual(target, service.health_url)
            return FakeResponse()

        with patch("app.status.urlopen", side_effect=open_response):
            result = check_service(service, timeout=1.0)

        self.assertTrue(result.ok)
        self.assertIsNotNone(result.homepage)
        assert result.homepage is not None
        self.assertTrue(result.homepage.ok)
        self.assertEqual(result.homepage.format, "json")
        self.assertEqual(result.homepage.report["name"], "Clear")

    def test_html_homepage_uses_metadata_without_returning_markup(self) -> None:
        body = b"""<!doctype html><html><head>
            <title>Safebox Home</title>
            <meta name="description" content="Your local Safebox">
            </head><body><script>private()</script></body></html>"""
        with patch(
            "app.status.urlopen",
            return_value=FakeResponse(body, content_type="text/html; charset=utf-8"),
        ):
            result = inspect_homepage("http://safebox-web:8000/", timeout=1.0)

        self.assertTrue(result.ok)
        self.assertEqual(
            result.report,
            {"title": "Safebox Home", "description": "Your local Safebox"},
        )
        self.assertNotIn("<script>", json.dumps(result.to_dict()))

    def test_oversized_homepage_is_rejected(self) -> None:
        body = b"x" * (MAX_HOMEPAGE_BYTES + 1)
        with patch("app.status.urlopen", return_value=FakeResponse(body)):
            result = inspect_homepage("http://grove:8000/", timeout=1.0)

        self.assertFalse(result.ok)
        self.assertEqual(result.detail, "homepage response is too large")


if __name__ == "__main__":
    unittest.main()
