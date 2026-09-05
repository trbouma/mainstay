from __future__ import annotations

import json
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from html.parser import HTMLParser
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from .registry import BundleConfig, ServiceEndpoint

MAX_HOMEPAGE_BYTES = 64 * 1024
MAX_REPORT_DEPTH = 4
MAX_REPORT_ITEMS = 24
MAX_REPORT_STRING = 500
SERVICE_IDENTITY_FIELDS = ("npub", "type", "management", "state")


@dataclass(frozen=True)
class HomepageResult:
    target: str
    ok: bool
    format: str = ""
    report: Any = None
    detail: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "target": self.target,
            "ok": self.ok,
            "format": self.format,
            "report": self.report,
            "detail": self.detail,
        }


@dataclass(frozen=True)
class HealthResult:
    name: str
    target: str
    ok: bool
    detail: str = ""
    homepage: HomepageResult | None = None


def check_bundle(bundle: BundleConfig, *, timeout: float) -> list[HealthResult]:
    services = [service for service in bundle.services.values() if service.enabled]
    if not services:
        return []
    with ThreadPoolExecutor(max_workers=min(8, len(services))) as executor:
        return list(
            executor.map(
                lambda service: check_service(service, timeout=timeout), services
            )
        )


def check_service(service: ServiceEndpoint, *, timeout: float) -> HealthResult:
    target = service.health_url
    if not target:
        fallback = service.url_for("internal") or service.name
        return HealthResult(service.name, fallback, False, "no health_url")
    if not target.startswith(("http://", "https://")):
        return HealthResult(service.name, target, False, "health_url is not HTTP")
    try:
        with urlopen(target, timeout=timeout) as response:
            if 200 <= response.status < 300:
                homepage = (
                    inspect_homepage(service.homepage_url, timeout=timeout)
                    if service.homepage_url
                    else None
                )
                return HealthResult(service.name, target, True, homepage=homepage)
            return HealthResult(service.name, target, False, f"HTTP {response.status}")
    except HTTPError as exc:
        return HealthResult(service.name, target, False, f"HTTP {exc.code}")
    except URLError as exc:
        return HealthResult(service.name, target, False, str(exc.reason))
    except TimeoutError:
        return HealthResult(service.name, target, False, "timeout")


def inspect_homepage(target: str, *, timeout: float) -> HomepageResult:
    if not target.startswith(("http://", "https://")):
        return HomepageResult(target, False, detail="homepage_url is not HTTP")

    request = Request(
        target,
        headers={
            "Accept": "application/json, text/html;q=0.8",
            "User-Agent": "mainstay-local",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            if not 200 <= response.status < 300:
                return HomepageResult(target, False, detail=f"HTTP {response.status}")
            body = response.read(MAX_HOMEPAGE_BYTES + 1)
            if len(body) > MAX_HOMEPAGE_BYTES:
                return HomepageResult(
                    target, False, detail="homepage response is too large"
                )
            content_type = response.headers.get("Content-Type", "").lower()
    except HTTPError as exc:
        return HomepageResult(target, False, detail=f"HTTP {exc.code}")
    except URLError as exc:
        return HomepageResult(target, False, detail=str(exc.reason))
    except TimeoutError:
        return HomepageResult(target, False, detail="timeout")

    text = body.decode("utf-8", errors="replace")
    if "json" in content_type or text.lstrip().startswith(("{", "[")):
        try:
            report = _normalize_report(json.loads(text))
        except json.JSONDecodeError:
            return HomepageResult(
                target, False, detail="invalid JSON homepage response"
            )
        return HomepageResult(target, True, format="json", report=report)

    if "html" in content_type or "<html" in text[:1000].lower():
        parser = _HomepageHTMLParser()
        parser.feed(text)
        report = {}
        if parser.title:
            report["title"] = parser.title
        if parser.description:
            report["description"] = parser.description
        if not report:
            return HomepageResult(
                target, False, detail="homepage has no summary metadata"
            )
        return HomepageResult(target, True, format="html", report=report)

    return HomepageResult(target, False, detail="unsupported homepage response")


def _normalize_report(value: Any, *, depth: int = 0) -> Any:
    if depth >= MAX_REPORT_DEPTH:
        return "..."
    if isinstance(value, dict):
        items = list(value.items())
        report = {}
        for key, item in items[:MAX_REPORT_ITEMS]:
            normalized_key = str(key)[:100]
            if depth == 0 and normalized_key == "service_identity":
                report[normalized_key] = _normalize_service_identity(item)
            else:
                report[normalized_key] = _normalize_report(
                    item, depth=depth + 1
                )
        if len(items) > MAX_REPORT_ITEMS:
            report["_truncated"] = True
        return report
    if isinstance(value, list):
        report = [
            _normalize_report(item, depth=depth + 1)
            for item in value[:MAX_REPORT_ITEMS]
        ]
        if len(value) > MAX_REPORT_ITEMS:
            report.append("...")
        return report
    if isinstance(value, str):
        return value[:MAX_REPORT_STRING]
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return str(value)[:MAX_REPORT_STRING]


def _normalize_service_identity(value: Any) -> dict[str, str | None]:
    if not isinstance(value, dict):
        return {}
    return {
        field: (
            None
            if value[field] is None
            else str(value[field])[:MAX_REPORT_STRING]
        )
        for field in SERVICE_IDENTITY_FIELDS
        if field in value
    }


class _HomepageHTMLParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.title = ""
        self.description = ""
        self._in_title = False
        self._title_parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "title":
            self._in_title = True
        if tag.lower() != "meta":
            return
        attributes = {name.lower(): value or "" for name, value in attrs}
        if attributes.get("name", "").lower() == "description":
            self.description = attributes.get("content", "")[:MAX_REPORT_STRING]

    def handle_endtag(self, tag: str) -> None:
        if tag.lower() == "title":
            self._in_title = False
            self.title = " ".join("".join(self._title_parts).split())[
                :MAX_REPORT_STRING
            ]

    def handle_data(self, data: str) -> None:
        if self._in_title:
            self._title_parts.append(data)
