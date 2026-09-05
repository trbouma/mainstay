from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

ENDPOINT_SCOPES = {"internal", "local", "external"}
LEGACY_PURPOSES = {
    "app": "web",
    "clear-mint": "mint",
    "blossom": "blossom",
    "nostr-relay": "relay",
}


@dataclass(frozen=True)
class EndpointAddress:
    scope: str
    purpose: str
    url: str
    priority: int = 100

    def __post_init__(self) -> None:
        if self.scope not in ENDPOINT_SCOPES:
            raise ValueError(f"unsupported endpoint scope: {self.scope}")
        if not self.purpose:
            raise ValueError("endpoint purpose must not be empty")
        if not self.url:
            raise ValueError("endpoint URL must not be empty")

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> EndpointAddress:
        return cls(
            scope=str(data["scope"]),
            purpose=str(data.get("purpose", "service")),
            url=str(data["url"]),
            priority=int(data.get("priority", 100)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "scope": self.scope,
            "purpose": self.purpose,
            "url": self.url,
            "priority": self.priority,
        }


@dataclass(frozen=True)
class ServiceEndpoint:
    name: str
    kind: str
    endpoints: tuple[EndpointAddress, ...]
    enabled: bool = True
    bind_address: str | None = None
    port: int | None = None
    fips_npub: str | None = None
    fips_port: int | None = None
    health_url: str | None = None
    homepage_url: str | None = None

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> ServiceEndpoint:
        endpoint_data = data.get("endpoints")
        if endpoint_data is None:
            endpoints = _legacy_endpoints(data)
        else:
            if not isinstance(endpoint_data, list):
                raise ValueError(f"services.{name}.endpoints must be a list")
            endpoints = tuple(
                EndpointAddress.from_dict(endpoint)
                for endpoint in endpoint_data
                if isinstance(endpoint, dict)
            )
            if len(endpoints) != len(endpoint_data):
                raise ValueError(
                    f"services.{name}.endpoints entries must be mappings"
                )
        return cls(
            name=name,
            kind=str(data["kind"]),
            endpoints=endpoints,
            enabled=bool(data.get("enabled", True)),
            bind_address=data.get("bind_address"),
            port=data.get("port"),
            fips_npub=data.get("fips_npub"),
            fips_port=data.get("fips_port"),
            health_url=data.get("health_url"),
            homepage_url=data.get("homepage_url"),
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "kind": self.kind,
            "enabled": self.enabled,
            "endpoints": [endpoint.to_dict() for endpoint in self.endpoints],
            "fips_npub": self.fips_npub,
            "fips_port": self.fips_port,
        }
        if self.bind_address is not None:
            data["bind_address"] = self.bind_address
        if self.port is not None:
            data["port"] = self.port
        if self.health_url is not None:
            data["health_url"] = self.health_url
        if self.homepage_url is not None:
            data["homepage_url"] = self.homepage_url
        return data

    def url_for(self, scope: str, *, purpose: str | None = None) -> str | None:
        candidates = [
            endpoint
            for endpoint in self.endpoints
            if endpoint.scope == scope
            and (purpose is None or endpoint.purpose == purpose)
        ]
        if not candidates:
            return None
        return min(candidates, key=lambda endpoint: endpoint.priority).url

    def require_url(self, scope: str, *, purpose: str | None = None) -> str:
        url = self.url_for(scope, purpose=purpose)
        if url is None:
            qualifier = f" {purpose}" if purpose else ""
            raise ValueError(
                f"service {self.name} has no {scope}{qualifier} endpoint"
            )
        return url

    def preferred_url(
        self,
        scopes: tuple[str, ...] = ("external", "local", "internal"),
        *,
        purpose: str | None = None,
    ) -> str:
        for scope in scopes:
            url = self.url_for(scope, purpose=purpose)
            if url is not None:
                return url
        qualifier = f" {purpose}" if purpose else ""
        raise ValueError(f"service {self.name} has no{qualifier} endpoint")


def _legacy_endpoints(data: dict[str, Any]) -> tuple[EndpointAddress, ...]:
    endpoints = []
    purpose = LEGACY_PURPOSES.get(str(data.get("kind")), "service")
    if data.get("local_url"):
        endpoints.append(
            EndpointAddress(
                scope="internal",
                purpose=purpose,
                url=str(data["local_url"]),
                priority=10,
            )
        )
    if data.get("advertised_url"):
        endpoints.append(
            EndpointAddress(
                scope="local",
                purpose=purpose,
                url=str(data["advertised_url"]),
                priority=20,
            )
        )
    return tuple(endpoints)


@dataclass(frozen=True)
class BundleConfig:
    name: str = "mainstay-local"
    host: str = "0.0.0.0"
    port: int = 8788
    forwarded_allow_ips: str = "127.0.0.1"
    clear_currency_name: str = "Mainstay Local Credits"
    secrets: dict[str, str] = field(default_factory=dict)
    services: dict[str, ServiceEndpoint] = field(default_factory=dict)

    @classmethod
    def default(cls) -> BundleConfig:
        return cls(
            secrets={
                "safebox_cookie_key": "",
                "safebox_onboard_invite_code": "",
                "clear_master_secret": "",
                "clear_operator_token": "",
            },
            services={
                "safebox_web": ServiceEndpoint(
                    name="safebox_web",
                    kind="app",
                    endpoints=(
                        EndpointAddress(
                            "internal", "web", "http://safebox-web:8000", 10
                        ),
                        EndpointAddress(
                            "local", "web", "http://127.0.0.1:8888", 20
                        ),
                    ),
                    enabled=True,
                    bind_address="0.0.0.0",
                    port=8888,
                    health_url="http://safebox-web:8000/health",
                    homepage_url="http://safebox-web:8000/",
                ),
                "clear": ServiceEndpoint(
                    name="clear",
                    kind="clear-mint",
                    endpoints=(
                        EndpointAddress(
                            "internal", "mint", "http://clear:3339", 10
                        ),
                    ),
                    health_url="http://clear:3339/health",
                    homepage_url="http://clear:3339/",
                ),
                "grove": ServiceEndpoint(
                    name="grove",
                    kind="blossom",
                    endpoints=(
                        EndpointAddress(
                            "internal", "blossom", "http://grove:8000", 10
                        ),
                    ),
                    health_url="http://grove:8000/health",
                    homepage_url="http://grove:8000/",
                ),
                "spurline": ServiceEndpoint(
                    name="spurline",
                    kind="nostr-relay",
                    endpoints=(
                        EndpointAddress(
                            "internal", "relay", "ws://spurline:8080", 10
                        ),
                    ),
                    health_url="http://spurline:8080/health",
                    homepage_url="http://spurline:8080/",
                ),
            },
        )

    @classmethod
    def from_json(cls, path: Path) -> BundleConfig:
        raw = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(raw, dict):
            raise ValueError(f"{path} must contain a mapping")

        service_map = raw.get("services") or {}
        if not isinstance(service_map, dict):
            raise ValueError("services must be a mapping")

        services = {
            name: ServiceEndpoint.from_dict(name, data)
            for name, data in service_map.items()
        }
        return cls(
            name=str(raw.get("name", "mainstay-local")),
            host=str(raw.get("host", "0.0.0.0")),
            port=int(raw.get("port", 8788)),
            forwarded_allow_ips=str(raw.get("forwarded_allow_ips", "127.0.0.1")),
            clear_currency_name=str(
                raw.get("clear_currency_name", "Mainstay Local Credits")
            ),
            secrets=dict(raw.get("secrets") or {}),
            services=services,
        )

    def to_json(self) -> str:
        data = {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "forwarded_allow_ips": self.forwarded_allow_ips,
            "clear_currency_name": self.clear_currency_name,
            "secrets": self.secrets,
            "services": {
                name: endpoint.to_dict()
                for name, endpoint in self.services.items()
            },
        }
        return json.dumps(data, indent=2) + "\n"

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "host": self.host,
            "port": self.port,
            "forwarded_allow_ips": self.forwarded_allow_ips,
            "clear_currency_name": self.clear_currency_name,
            "services": {
                name: endpoint.to_dict()
                for name, endpoint in self.services.items()
            },
        }

    def require_service(self, name: str) -> ServiceEndpoint:
        try:
            return self.services[name]
        except KeyError as exc:
            raise ValueError(f"missing required service: {name}") from exc
