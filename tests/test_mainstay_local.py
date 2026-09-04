from __future__ import annotations

import unittest

from app.env import render_safebox_env
from app.registry import BundleConfig


class MainstayLocalTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
