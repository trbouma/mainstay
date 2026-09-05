from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from app.cli import DEFAULT_COMPOSE_PATH, _up
from app.env import render_safebox_env
from app.registry import BundleConfig, EndpointAddress, ServiceEndpoint
from app.server import render_dashboard


class MainstayLocalTests(unittest.TestCase):
    def test_compose_is_owned_by_mainstay(self) -> None:
        self.assertEqual(DEFAULT_COMPOSE_PATH, Path("docker-compose.yaml"))

    def test_default_registry_renders_safebox_env(self) -> None:
        env = render_safebox_env(BundleConfig.default())

        self.assertIn('SAFEBOX_DEFAULT_BOOTSTRAP_RELAY="ws://spurline:8080"', env)
        self.assertIn("SAFEBOX_ONBOARD_INVITE_CODE=", env)
        self.assertIn('SAFEBOX_ALLOW_INSECURE_HTTP="true"', env)
        self.assertIn('SAFEBOX_ALLOW_INSECURE_MINTS="true"', env)
        self.assertIn('MAINSTAY_SAFEBOX_BIND_ADDRESS="0.0.0.0"', env)
        self.assertIn('MAINSTAY_SAFEBOX_PORT="8888"', env)
        self.assertIn('SAFEBOX_DEFAULT_HOME_MINT="http://clear:3339"', env)
        self.assertIn('SAFEBOX_BLOSSOM_HOME_SERVER="http://grove:8000"', env)
        self.assertIn('SPURLINE_PUBLIC_URL="ws://spurline:8080"', env)
        self.assertIn('CLEAR_MINT_URL="http://clear:3339"', env)
        self.assertIn('GROVE_PUBLIC_URL="http://grove:8000"', env)
        self.assertIn('CLEAR_CURRENCY_NAME="Mainstay Local Credits"', env)

    def test_default_registry_serializes_json(self) -> None:
        original = BundleConfig.default()
        text = original.to_json()
        self.assertIn('"name": "mainstay-local"', text)
        self.assertIn('"fips_npub"', text)
        self.assertIn('"homepage_url": "http://clear:3339/"', text)
        self.assertIn('"scope": "internal"', text)
        self.assertNotIn('"local_url"', text)

    def test_spurline_uses_the_private_runtime_namespace(self) -> None:
        bundle = BundleConfig.default()
        spurline = bundle.require_service("spurline")

        self.assertTrue(spurline.enabled)
        self.assertEqual(
            spurline.require_url("internal", purpose="relay"),
            "ws://spurline:8080",
        )
        self.assertEqual(spurline.health_url, "http://spurline:8080/health")
        self.assertEqual(spurline.homepage_url, "http://spurline:8080/")
        self.assertIsNone(spurline.url_for("local"))
        self.assertIsNone(spurline.url_for("external"))
        safebox_web = bundle.require_service("safebox_web")
        self.assertTrue(safebox_web.enabled)
        self.assertEqual(safebox_web.port, 8888)
        self.assertEqual(safebox_web.bind_address, "0.0.0.0")
        self.assertEqual(
            safebox_web.require_url("local", purpose="web"),
            "http://127.0.0.1:8888",
        )
        self.assertEqual(
            safebox_web.health_url, "http://safebox-web:8000/health"
        )

    def test_clear_uses_the_private_runtime_namespace(self) -> None:
        clear = BundleConfig.default().require_service("clear")

        self.assertTrue(clear.enabled)
        self.assertEqual(
            clear.require_url("internal", purpose="mint"),
            "http://clear:3339",
        )
        self.assertIsNone(clear.url_for("local"))
        self.assertIsNone(clear.url_for("external"))
        self.assertEqual(clear.health_url, "http://clear:3339/health")
        self.assertEqual(clear.homepage_url, "http://clear:3339/")

    def test_grove_uses_the_private_runtime_namespace(self) -> None:
        grove = BundleConfig.default().require_service("grove")

        self.assertTrue(grove.enabled)
        self.assertEqual(
            grove.require_url("internal", purpose="blossom"),
            "http://grove:8000",
        )
        self.assertIsNone(grove.url_for("local"))
        self.assertIsNone(grove.url_for("external"))
        self.assertEqual(grove.health_url, "http://grove:8000/health")
        self.assertEqual(grove.homepage_url, "http://grove:8000/")

    def test_dashboard_lists_services_and_api_endpoints(self) -> None:
        page = render_dashboard(BundleConfig.default())

        self.assertIn("There's no place like home.", page)
        self.assertIn('data-service="safebox_web"', page)
        self.assertIn('href="/registry"', page)
        self.assertIn('fetch("/status"', page)
        self.assertIn("window.location.hostname", page)
        self.assertIn('class="service-report"', page)
        self.assertIn("description.textContent", page)
        self.assertEqual(page.count("Local</span>"), 1)
        self.assertNotIn("External</span>", page)

    def test_dashboard_escapes_registry_values(self) -> None:
        bundle = BundleConfig(
            name="<unsafe>",
            services={
                "service<script>": ServiceEndpoint(
                    name="service<script>",
                    kind="app&tool",
                    endpoints=(
                        EndpointAddress(
                            "internal",
                            "service",
                            "http://service/?left=1&right=2",
                        ),
                        EndpointAddress(
                            "external",
                            "service",
                            "https://example.test/?left=1&right=2",
                        ),
                    ),
                )
            },
        )

        page = render_dashboard(bundle)

        self.assertNotIn("<unsafe>", page)
        self.assertNotIn("service<script>", page)
        self.assertIn("&lt;unsafe&gt;", page)
        self.assertIn("app&amp;tool", page)

    def test_up_uses_the_default_service_set_without_a_profile(self) -> None:
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

    def test_legacy_registry_urls_migrate_to_scoped_endpoints(self) -> None:
        service = ServiceEndpoint.from_dict(
            "legacy",
            {
                "kind": "app",
                "local_url": "http://legacy:8000",
                "advertised_url": "http://127.0.0.1:8000",
            },
        )

        self.assertEqual(
            service.url_for("internal", purpose="web"),
            "http://legacy:8000",
        )
        self.assertEqual(
            service.url_for("local", purpose="web"),
            "http://127.0.0.1:8000",
        )
        self.assertNotIn("local_url", service.to_dict())

    def test_external_clear_hint_does_not_change_safebox_internal_url(self) -> None:
        original = BundleConfig.default()
        services = dict(original.services)
        clear = services["clear"]
        services["clear"] = ServiceEndpoint(
            name=clear.name,
            kind=clear.kind,
            endpoints=clear.endpoints
            + (
                EndpointAddress(
                    "external", "mint", "https://mint.safebox.dev", 30
                ),
            ),
            health_url=clear.health_url,
            homepage_url=clear.homepage_url,
        )

        env = render_safebox_env(BundleConfig(services=services))

        self.assertIn('SAFEBOX_DEFAULT_HOME_MINT="http://clear:3339"', env)
        self.assertIn('CLEAR_MINT_URL="https://mint.safebox.dev"', env)

    def test_endpoint_priority_selects_the_lowest_value_within_a_scope(self) -> None:
        service = ServiceEndpoint(
            name="clear",
            kind="clear-mint",
            endpoints=(
                EndpointAddress("external", "mint", "https://backup.test", 50),
                EndpointAddress("external", "mint", "https://primary.test", 10),
            ),
        )

        self.assertEqual(
            service.preferred_url(purpose="mint"),
            "https://primary.test",
        )

    def test_endpoint_scope_must_be_known(self) -> None:
        with self.assertRaisesRegex(ValueError, "unsupported endpoint scope"):
            EndpointAddress("public", "mint", "https://mint.example")


if __name__ == "__main__":
    unittest.main()
