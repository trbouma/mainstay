from __future__ import annotations

from dataclasses import dataclass
from urllib.error import HTTPError, URLError
from urllib.request import urlopen

from .registry import BundleConfig, ServiceEndpoint


@dataclass(frozen=True)
class HealthResult:
    name: str
    target: str
    ok: bool
    detail: str = ""


def check_bundle(bundle: BundleConfig, *, timeout: float) -> list[HealthResult]:
    return [
        check_service(service, timeout=timeout)
        for service in bundle.services.values()
        if service.enabled
    ]


def check_service(service: ServiceEndpoint, *, timeout: float) -> HealthResult:
    target = service.health_url
    if not target:
        return HealthResult(service.name, service.local_url, False, "no health_url")
    if not target.startswith(("http://", "https://")):
        return HealthResult(service.name, target, False, "health_url is not HTTP")
    try:
        with urlopen(target, timeout=timeout) as response:
            if 200 <= response.status < 300:
                return HealthResult(service.name, target, True)
            return HealthResult(service.name, target, False, f"HTTP {response.status}")
    except HTTPError as exc:
        return HealthResult(service.name, target, False, f"HTTP {exc.code}")
    except URLError as exc:
        return HealthResult(service.name, target, False, str(exc.reason))
    except TimeoutError:
        return HealthResult(service.name, target, False, "timeout")
