from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class ServiceEndpoint:
    name: str
    kind: str
    local_url: str
    advertised_url: str
    enabled: bool = True
    bind_address: str | None = None
    port: int | None = None
    fips_npub: str | None = None
    fips_port: int | None = None
    health_url: str | None = None

    @classmethod
    def from_dict(cls, name: str, data: dict[str, Any]) -> ServiceEndpoint:
        return cls(
            name=name,
            kind=str(data["kind"]),
            local_url=str(data["local_url"]),
            advertised_url=str(data.get("advertised_url") or data["local_url"]),
            enabled=bool(data.get("enabled", True)),
            bind_address=data.get("bind_address"),
            port=data.get("port"),
            fips_npub=data.get("fips_npub"),
            fips_port=data.get("fips_port"),
            health_url=data.get("health_url"),
        )

    def to_dict(self) -> dict[str, Any]:
        data: dict[str, Any] = {
            "kind": self.kind,
            "enabled": self.enabled,
            "local_url": self.local_url,
            "advertised_url": self.advertised_url,
            "fips_npub": self.fips_npub,
            "fips_port": self.fips_port,
        }
        if self.bind_address is not None:
            data["bind_address"] = self.bind_address
        if self.port is not None:
            data["port"] = self.port
        if self.health_url is not None:
            data["health_url"] = self.health_url
        return data


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
                "clear_master_secret": "",
                "clear_operator_token": "",
            },
            services={
                "safebox_web": ServiceEndpoint(
                    name="safebox_web",
                    kind="app",
                    local_url="http://safebox-web:8000",
                    advertised_url="http://127.0.0.1:8000",
                    enabled=False,
                    bind_address="127.0.0.1",
                    port=8000,
                    health_url="http://127.0.0.1:8000/health",
                ),
                "clear": ServiceEndpoint(
                    name="clear",
                    kind="clear-mint",
                    local_url="http://clear:3339",
                    advertised_url="http://clear:3339",
                    enabled=False,
                    health_url="http://127.0.0.1:3339/health",
                ),
                "grove": ServiceEndpoint(
                    name="grove",
                    kind="blossom",
                    local_url="http://grove:8000",
                    advertised_url="http://grove:8000",
                    enabled=False,
                    health_url="http://127.0.0.1:8001/health",
                ),
                "spurline": ServiceEndpoint(
                    name="spurline",
                    kind="nostr-relay",
                    local_url="ws://spurline:8080",
                    advertised_url="ws://spurline:8080",
                    health_url="http://spurline:8080/health",
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
