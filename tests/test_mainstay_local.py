from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from app.cli import DEFAULT_COMPOSE_PATH, _up
from app.env import render_safebox_env
from app.registry import BundleConfig, ServiceEndpoint
from app.server import render_dashboard


class MainstayLocalTests(unittest.TestCase):
    def test_compose_is_owned_by_mainstay(self) -> None:
        self.assertEqual(DEFAULT_COMPOSE_PATH, Path("docker-compose.yaml"))

    def test_default_registry_renders_safebox_env(self) -> None:
        env = render_safebox_env(BundleConfig.default())

        self.assertIn('SAFEBOX_DEFAULT_BOOTSTRAP_RELAY="ws://spurline:8080"', env)
        self.assertIn('SAFEBOX_DEFAULT_HOME_MINT="http://clear:3339"', env)
        self.assertIn('SAFEBOX_BLOSSOM_HOME_SERVER="http://grove:8000"', env)
        self.assertIn('CLEAR_CURRENCY_NAME="Mainstay Local Credits"', env)

    def test_default_registry_serializes_json(self) -> None:
        original = BundleConfig.default()
        text = original.to_json()
        self.assertIn('"name": "mainstay-local"', text)
        self.assertIn('"fips_npub"', text)

    def test_spurline_uses_the_private_runtime_namespace(self) -> None:
        bundle = BundleConfig.default()
        spurline = bundle.require_service("spurline")

        self.assertTrue(spurline.enabled)
        self.assertEqual(spurline.local_url, "ws://spurline:8080")
        self.assertEqual(spurline.health_url, "http://spurline:8080/health")
        self.assertFalse(bundle.require_service("safebox_web").enabled)

    def test_clear_uses_the_private_runtime_namespace(self) -> None:
        clear = BundleConfig.default().require_service("clear")

        self.assertTrue(clear.enabled)
        self.assertEqual(clear.local_url, "http://clear:3339")
        self.assertEqual(clear.advertised_url, "http://clear:3339")
        self.assertEqual(clear.health_url, "http://clear:3339/health")

    def test_grove_uses_the_private_runtime_namespace(self) -> None:
        grove = BundleConfig.default().require_service("grove")

        self.assertTrue(grove.enabled)
        self.assertEqual(grove.local_url, "http://grove:8000")
        self.assertEqual(grove.advertised_url, "http://grove:8000")
        self.assertEqual(grove.health_url, "http://grove:8000/health")

    def test_dashboard_lists_services_and_api_endpoints(self) -> None:
        page = render_dashboard(BundleConfig.default())

        self.assertIn("There's no place like home.", page)
        self.assertIn('data-service="safebox_web"', page)
        self.assertIn('href="/registry"', page)
        self.assertIn('fetch("/status"', page)
        self.assertIn("window.location.hostname", page)

    def test_dashboard_escapes_registry_values(self) -> None:
        bundle = BundleConfig(
            name="<unsafe>",
            services={
                "service<script>": ServiceEndpoint(
                    name="service<script>",
                    kind="app&tool",
                    local_url="http://service/?left=1&right=2",
                    advertised_url="https://example.test/?left=1&right=2",
                )
            },
        )

        page = render_dashboard(bundle)

        self.assertNotIn("<unsafe>", page)
        self.assertNotIn("service<script>", page)
        self.assertIn("&lt;unsafe&gt;", page)
        self.assertIn("app&amp;tool", page)

    def test_up_does_not_enable_safebox_web_by_default(self) -> None:
        bundle = BundleConfig.default()
        with (
            patch("app.cli.BundleConfig.from_json", return_value=bundle),
            patch("app.cli._config"),
            patch("app.cli.subprocess.call", return_value=0) as call,
        ):
            result = _up(
                Path("mainstay-local.json"),
                Path("docker-compose.yaml"),
                Path("safebox-web.env"),
                True,
            )

        self.assertEqual(result, 0)
        command = call.call_args.args[0]
        self.assertNotIn("--profile", command)

    def test_up_enables_safebox_web_only_when_registry_enables_it(self) -> None:
        original = BundleConfig.default()
        services = dict(original.services)
        current = services["safebox_web"]
        services["safebox_web"] = ServiceEndpoint(
            name=current.name,
            kind=current.kind,
            local_url=current.local_url,
            advertised_url=current.advertised_url,
            enabled=True,
            bind_address=current.bind_address,
            port=current.port,
            health_url=current.health_url,
        )
        bundle = BundleConfig(services=services)
        with (
            patch("app.cli.BundleConfig.from_json", return_value=bundle),
            patch("app.cli._config"),
            patch("app.cli.subprocess.call", return_value=0) as call,
        ):
            _up(
                Path("mainstay-local.json"),
                Path("docker-compose.yaml"),
                Path("safebox-web.env"),
                False,
            )

        command = call.call_args.args[0]
        self.assertIn("--profile", command)
        self.assertIn("safebox-web", command)


if __name__ == "__main__":
    unittest.main()
