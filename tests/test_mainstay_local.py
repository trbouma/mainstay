from __future__ import annotations

import os
import unittest
from pathlib import Path
from unittest.mock import patch

from stroma import Keys, fips_ipv6_address

from app.cli import DEFAULT_COMPOSE_PATH, _serve, _up
from app.env import render_safebox_env
from app.registry import BundleConfig, EndpointAddress, ServiceEndpoint
from app.server import (
    installation_identity,
    render_dashboard,
    render_service_context,
)
from app.status import HomepageResult


class MainstayLocalTests(unittest.TestCase):
    def test_compose_is_owned_by_mainstay(self) -> None:
        self.assertEqual(DEFAULT_COMPOSE_PATH, Path("docker-compose.yaml"))

    def test_service_acorn_worker_is_in_the_default_compose_bundle(self) -> None:
        compose = (Path(__file__).parents[1] / DEFAULT_COMPOSE_PATH).read_text(
            encoding="utf-8"
        )

        self.assertNotIn('profiles: ["service-acorn"]', compose)
        self.assertIn('SAFEBOX_SERVICE_ACORN_ENABLED: "true"', compose)
        self.assertIn(
            'SAFEBOX_NIP05_EXTERNAL_RELAYS: "${SAFEBOX_NIP05_EXTERNAL_RELAYS:-}"',
            compose,
        )
        env_example = (Path(__file__).parents[1] / ".env.example").read_text(
            encoding="utf-8"
        )
        self.assertIn(
            "SAFEBOX_NIP05_EXTERNAL_RELAYS=wss://spurline.safebox.dev",
            env_example,
        )
        self.assertIn(
            'SAFEBOX_CLEAR_EXTERNAL_MINTS: "${MAINSTAY_EXTERNAL_CLEAR_MINT_URL:-https://clear.safebox.dev}"',
            compose,
        )
        self.assertIn("service-acorn.json", compose)

    def test_component_images_use_remote_git_build_contexts(self) -> None:
        compose = (Path(__file__).parents[1] / DEFAULT_COMPOSE_PATH).read_text(
            encoding="utf-8"
        )

        for repository in ("safebox-web", "spurline", "grove", "clear"):
            self.assertIn(
                f"https://github.com/trbouma/{repository}.git#main",
                compose,
            )
        self.assertNotIn("context: ../", compose)

    def test_default_images_are_scoped_to_the_compose_project(self) -> None:
        compose = (Path(__file__).parents[1] / DEFAULT_COMPOSE_PATH).read_text(
            encoding="utf-8"
        )

        for suffix in ("control", "safebox-web", "spurline", "grove", "clear"):
            self.assertIn(
                "${COMPOSE_PROJECT_NAME:-mainstay-local}-"
                f"{suffix}:local",
                compose,
            )
        self.assertEqual(
            compose.count(
                "${SAFEBOX_IMAGE:-${COMPOSE_PROJECT_NAME:-mainstay-local}"
                "-safebox-web:local}"
            ),
            2,
        )

    def test_default_registry_renders_safebox_env(self) -> None:
        env = render_safebox_env(BundleConfig.default())

        self.assertIn('SAFEBOX_DEFAULT_BOOTSTRAP_RELAY="ws://spurline:8080"', env)
        self.assertIn("SAFEBOX_ONBOARD_INVITE_CODE=", env)
        self.assertIn("SAFEBOX_WEB_SERVICE_NSEC=", env)
        self.assertIn(
            'SAFEBOX_WEB_SERVICE_MANAGEMENT="mainstay-managed"', env
        )
        self.assertIn('SAFEBOX_ALLOW_INSECURE_HTTP="true"', env)
        self.assertIn('SAFEBOX_SERVICE_ACORN_ENABLED="true"', env)
        self.assertIn('MAINSTAY_SAFEBOX_BIND_ADDRESS="0.0.0.0"', env)
        self.assertIn('MAINSTAY_SAFEBOX_PORT="8888"', env)
        self.assertIn(
            'SAFEBOX_DEFAULT_HOME_MINT="https://mint.safebox.dev"', env
        )
        self.assertIn(
            'MAINSTAY_LIGHTNING_MINT_URL="https://mint.safebox.dev"', env
        )
        self.assertIn(
            'MAINSTAY_EXTERNAL_CLEAR_MINT_URL="https://clear.safebox.dev"',
            env,
        )
        self.assertIn(
            'SAFEBOX_CLEAR_MINTS="http://clear:3339,https://clear.safebox.dev"',
            env,
        )
        self.assertIn(
            'SAFEBOX_CLEAR_EXTERNAL_MINTS="https://clear.safebox.dev"',
            env,
        )
        self.assertIn('SAFEBOX_BLOSSOM_HOME_SERVER="http://grove:8000"', env)
        self.assertIn('SAFEBOX_CURRENCY_RATES_ENABLED="true"', env)
        self.assertIn(
            'SAFEBOX_CURRENCY_RATE_SOURCE_URL="https://blockchain.info/ticker"',
            env,
        )
        self.assertIn('SAFEBOX_CURRENCY_RATE_INTERVAL_SECONDS="3600"', env)
        self.assertIn('SAFEBOX_DEFAULT_DISPLAY_CURRENCY="USD"', env)
        self.assertIn('SAFEBOX_CURRENCY_RATE_STALE_SECONDS="86400"', env)
        self.assertIn(
            'SAFEBOX_MAINSTAY_CONTEXT_URL="http://mainstay-local:8788/context"',
            env,
        )
        self.assertIn('SPURLINE_PUBLIC_URL="ws://spurline:8080"', env)
        self.assertIn('CLEAR_MINT_URL="http://clear:3339"', env)
        self.assertIn("CLEAR_MINT_SERVICE_NSEC=", env)
        self.assertIn("SPURLINE_SERVICE_NSEC=", env)
        self.assertIn('SPURLINE_SERVICE_MANAGEMENT="mainstay-managed"', env)
        self.assertIn("GROVE_SERVICE_NSEC=", env)
        self.assertIn('GROVE_SERVICE_MANAGEMENT="mainstay-managed"', env)
        self.assertIn(
            'CLEAR_MINT_SERVICE_MANAGEMENT="mainstay-managed"', env
        )
        self.assertIn('GROVE_PUBLIC_URL="http://grove:8000"', env)
        self.assertIn('CLEAR_CURRENCY_NAME="Mainstay Local Credits"', env)

    def test_default_registry_serializes_json(self) -> None:
        original = BundleConfig.default()
        text = original.to_json()
        self.assertIn('"name": "mainstay-local"', text)
        self.assertIn(
            '"lightning_mint_url": "https://mint.safebox.dev"', text
        )
        self.assertIn(
            '"external_clear_mint_url": "https://clear.safebox.dev"', text
        )
        self.assertIn('"service_acorn_reserve_sats": 100', text)
        self.assertIn('"fips_npub"', text)
        self.assertIn('"homepage_url": "http://clear:3339/"', text)
        self.assertIn('"scope": "internal"', text)
        self.assertNotIn('"local_url"', text)
        self.assertNotIn("secrets", original.to_dict())

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
        self.assertEqual(
            safebox_web.homepage_url, "http://safebox-web:8000/info"
        )

    def test_default_registry_accepts_the_installed_safebox_port(self) -> None:
        safebox_web = BundleConfig.default(
            safebox_port=9000
        ).require_service("safebox_web")

        self.assertEqual(safebox_web.port, 9000)
        self.assertEqual(
            safebox_web.require_url("local", purpose="web"),
            "http://127.0.0.1:9000",
        )

    @patch("app.cli.serve")
    def test_server_uses_safebox_port_from_environment(self, serve) -> None:
        missing_config = Path("does-not-exist.json")

        with patch.dict(os.environ, {"MAINSTAY_SAFEBOX_PORT": "9000"}):
            result = _serve(missing_config, host=None, port=None)

        self.assertEqual(result, 0)
        bundle = serve.call_args.args[0]
        self.assertEqual(
            bundle.require_service("safebox_web").require_url(
                "local", purpose="web"
            ),
            "http://127.0.0.1:9000",
        )

    @patch("app.cli.serve")
    def test_server_uses_instance_display_name_from_environment(self, serve) -> None:
        missing_config = Path("does-not-exist.json")

        with patch.dict(
            os.environ,
            {"MAINSTAY_INSTANCE_NAME": "Cedar Resort"},
        ):
            result = _serve(missing_config, host=None, port=None)

        self.assertEqual(result, 0)
        bundle = serve.call_args.args[0]
        self.assertEqual(bundle.name, "Cedar Resort")

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

        compose = (Path(__file__).parents[1] / DEFAULT_COMPOSE_PATH).read_text(
            encoding="utf-8"
        )
        self.assertIn("CLEAR_MINT_SERVICE_NSEC", compose)
        self.assertIn("SAFEBOX_WEB_SERVICE_NSEC", compose)
        self.assertIn("SAFEBOX_WEB_SERVICE_MANAGEMENT", compose)
        self.assertEqual(
            compose.count(
                'SAFEBOX_CURRENCY_RATES_ENABLED: "'
                '${SAFEBOX_CURRENCY_RATES_ENABLED:-true}"'
            ),
            2,
        )
        self.assertIn("SAFEBOX_CURRENCY_RATE_SOURCE_URL", compose)
        self.assertIn("SAFEBOX_CURRENCY_RATE_INTERVAL_SECONDS", compose)
        self.assertIn("SAFEBOX_CURRENCY_RATE_CURRENCIES", compose)
        self.assertIn("SAFEBOX_CURRENCY_RATE_STALE_SECONDS", compose)
        self.assertIn('CLEAR_MINT_SERVICE_MANAGEMENT: "mainstay-managed"', compose)

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

        compose = (Path(__file__).parents[1] / DEFAULT_COMPOSE_PATH).read_text(
            encoding="utf-8"
        )
        self.assertIn("GROVE_SERVICE_NSEC", compose)
        self.assertIn('GROVE_SERVICE_MANAGEMENT: "mainstay-managed"', compose)

    @patch("app.server.inspect_homepage")
    def test_service_context_advertises_grove_identity_and_internal_route(
        self, inspect
    ) -> None:
        inspect.return_value = HomepageResult(
            "http://grove:8000/",
            True,
            format="json",
            report={
                "service_identity": {
                    "npub": "npub1grove",
                    "nsec": "must-not-escape",
                }
            },
        )

        context = render_service_context(
            BundleConfig.default(),
            installation_npub="npub1mainstay",
        )

        self.assertEqual(context["context_npub"], "npub1mainstay")
        self.assertEqual(context["services"][0]["service_npub"], "npub1grove")
        self.assertEqual(
            context["services"][0]["endpoints"][0]["locator"]["url"],
            "http://grove:8000",
        )
        self.assertNotIn("nsec", str(context))

    def test_spurline_uses_a_managed_service_identity(self) -> None:
        compose = (Path(__file__).parents[1] / DEFAULT_COMPOSE_PATH).read_text(
            encoding="utf-8"
        )

        self.assertIn("SPURLINE_SERVICE_NSEC", compose)
        self.assertIn('SPURLINE_SERVICE_MANAGEMENT: "mainstay-managed"', compose)

    def test_dashboard_lists_services_and_api_endpoints(self) -> None:
        page = render_dashboard(BundleConfig.default())

        self.assertIn("There&#x27;s no place like home.", page)
        self.assertIn('<html lang="en" dir="ltr">', page)
        self.assertIn('<select id="language" name="lang"', page)
        self.assertIn('<option value="en" selected>English</option>', page)
        self.assertIn('data-service="safebox_web"', page)
        self.assertIn('href="registry"', page)
        self.assertIn('fetch("status"', page)
        self.assertNotIn('href="/', page)
        self.assertNotIn('src="/', page)
        self.assertNotIn('fetch("/', page)
        self.assertIn("window.location.hostname", page)
        self.assertIn('class="service-report"', page)
        self.assertIn('class="service-identity" hidden', page)
        self.assertIn('class="identity-npub technical"', page)
        self.assertIn('class="fips-label fips-field"', page)
        self.assertIn('class="identity-fips fips-field technical"', page)
        self.assertIn('class="operator-npub operator-field technical"', page)
        self.assertIn("operator.status", page)
        self.assertIn("renderIdentity", page)
        self.assertIn("identity.fips_ipv6_address", page)
        self.assertIn('name !== "service_identity"', page)
        self.assertIn("description.textContent", page)
        self.assertIn("Required bootstrap step", page)
        self.assertIn("Confirm Lightning fee reserve", page)
        self.assertIn("app.service_acorn_worker fund 100", page)
        self.assertIn("./reserve-balance.sh", page)
        self.assertIn("does not yet measure the reserve automatically", page)
        self.assertEqual(page.count("Local</span>"), 1)
        self.assertNotIn("External</span>", page)

    def test_dashboard_presents_mainstay_installation_identity(self) -> None:
        npub = Keys(priv_k="33" * 32).public_key_bech32()

        page = render_dashboard(
            BundleConfig.default(),
            installation_npub=npub,
        )
        identity = installation_identity(npub)

        assert identity is not None
        self.assertIn('src="assets/mainstay-logo.svg"', page)
        self.assertIn('href="identity"', page)
        self.assertIn("Mainstay installation", page)
        self.assertIn(npub, page)
        self.assertIn(fips_ipv6_address(npub), page)
        self.assertEqual(identity["type"], "mainstay-installation")
        self.assertEqual(identity["role"], "installation and control plane")

    def test_dashboard_omits_reserve_advisory_without_safebox(self) -> None:
        bundle = BundleConfig(
            services={
                "clear": BundleConfig.default().require_service("clear"),
            }
        )

        page = render_dashboard(bundle)

        self.assertNotIn("Confirm Lightning fee reserve", page)

    def test_service_acorn_reserve_must_be_positive(self) -> None:
        with self.assertRaisesRegex(
            ValueError, "service_acorn_reserve_sats must be positive"
        ):
            BundleConfig(service_acorn_reserve_sats=0)

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

    def test_external_clear_hint_does_not_replace_the_lightning_mint(self) -> None:
        original = BundleConfig.default()
        services = dict(original.services)
        clear = services["clear"]
        services["clear"] = ServiceEndpoint(
            name=clear.name,
            kind=clear.kind,
            endpoints=clear.endpoints
            + (
                EndpointAddress(
                    "external", "mint", "https://clear.example", 30
                ),
            ),
            health_url=clear.health_url,
            homepage_url=clear.homepage_url,
        )

        env = render_safebox_env(BundleConfig(services=services))

        self.assertIn(
            'SAFEBOX_DEFAULT_HOME_MINT="https://mint.safebox.dev"', env
        )
        self.assertIn('CLEAR_MINT_URL="https://clear.example"', env)

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
