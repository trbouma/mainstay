from __future__ import annotations

import pytest

from app.localization import (
    DEFAULT_LANGUAGE,
    SUPPORTED_LANGUAGES,
    normalize_language_tag,
    resolve_language,
    supported_language,
    translator,
)
from app.registry import BundleConfig
from app.server import _handler_for, render_dashboard


def test_language_tags_are_canonicalized() -> None:
    assert normalize_language_tag("FR-ca") == "fr-CA"
    assert normalize_language_tag("zh-hans") == "zh-Hans"


def test_supported_language_uses_reviewed_aliases_and_safe_fallback() -> None:
    assert supported_language("es-MX") == "es"
    assert supported_language("de-AT") == "de"
    assert supported_language("zh-CN") == "zh-Hans"
    assert supported_language("zh-Hans-CN") == "zh-Hans"
    assert supported_language("zh-TW") == DEFAULT_LANGUAGE
    assert supported_language("../fr") == DEFAULT_LANGUAGE


def test_explicit_language_precedes_browser_preference() -> None:
    assert resolve_language("it", "fr-CA,fr;q=0.9") == "it"
    assert resolve_language("zh-CN", "en") == "zh-Hans"


def test_browser_language_uses_quality_and_supported_fallback() -> None:
    assert resolve_language(None, "nl;q=1,de-AT;q=0.8,en;q=0.5") == "de"
    assert resolve_language(None, "nl,pt-BR;q=0.8") == "pt"
    assert resolve_language(None, "zh-CN,en;q=0.5") == "zh-Hans"


@pytest.mark.parametrize(
    ("language", "translated_label"),
    [
        ("fr", "Réseau de services"),
        ("es", "Red de servicios"),
        ("pt", "Rede de serviços"),
        ("de", "Dienstnetzwerk"),
        ("it", "Rete di servizi"),
        ("zh-Hans", "服务网络"),
    ],
)
def test_each_catalog_translates_the_dashboard(
    language: str,
    translated_label: str,
) -> None:
    assert translator(language)("service_network") == translated_label
    assert language in SUPPORTED_LANGUAGES


@pytest.mark.parametrize("language", SUPPORTED_LANGUAGES)
def test_dashboard_renders_every_supported_language(language: str) -> None:
    bundle = BundleConfig.default()
    page = render_dashboard(
        bundle,
        installation_npub="npub1mainstay",
        language=language,
    )

    assert f'<html lang="{language}">' in page
    assert f'<option value="{language}" selected>' in page
    assert bundle.name in page
    assert "npub1mainstay" in page
    assert "http://clear:3339" in page
    assert 'fetch("status"' in page
    assert 'const documentLanguage = ' in page


def test_render_dashboard_normalizes_a_supported_language_alias() -> None:
    page = render_dashboard(BundleConfig.default(), language="zh-CN")

    assert '<html lang="zh-Hans">' in page
    assert '<option value="zh-Hans" selected>简体中文</option>' in page
    assert "服务网络" in page


def test_dashboard_route_resolves_query_language_and_sets_headers() -> None:
    handler_type = _handler_for(BundleConfig.default())
    handler = object.__new__(handler_type)
    handler.path = "/?lang=fr"
    handler.headers = {"Accept-Language": "de"}
    captured: dict[str, object] = {}

    def capture_response(text: str, **options: object) -> None:
        captured["text"] = text
        captured.update(options)

    handler._send_text = capture_response
    handler.do_GET()

    assert '<html lang="fr">' in str(captured["text"])
    assert captured["headers"] == {
        "Content-Language": "fr",
        "Vary": "Accept-Language",
    }


def test_unknown_message_key_falls_back_without_mutating_protocol_text() -> None:
    german = translator("de")

    assert german("unknown.protocol.value") == "unknown.protocol.value"
