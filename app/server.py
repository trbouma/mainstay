# The self-contained dashboard keeps its CSS and JavaScript readable in-place.
# ruff: noqa: E501

from __future__ import annotations

import json
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from stroma import fips_ipv6_address

from . import __version__
from .registry import BundleConfig, ServiceEndpoint
from .status import check_bundle, inspect_homepage

GROVE_CAPABILITIES = ("blossom.read", "blossom.write", "blossom.delete")


def render_dashboard(
    bundle: BundleConfig,
    *,
    installation_npub: str | None = None,
) -> str:
    service_rows = "\n".join(
        _render_service_row(name, endpoint)
        for name, endpoint in bundle.services.items()
    )
    reserve_advisory = _render_reserve_advisory(bundle)
    installation_panel = _render_installation_panel(
        bundle,
        installation_npub=installation_npub,
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="color-scheme" content="light">
  <title>{escape(bundle.name)} | Mainstay Local</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #14201c;
      --muted: #607069;
      --line: #d5ddd8;
      --surface: #ffffff;
      --canvas: #eef3f0;
      --deep: #12312c;
      --deep-soft: #1c443c;
      --accent: #087b62;
      --blue: #2774a6;
      --amber: #e4a53a;
      --coral: #c95f4d;
      --warning: #a15c00;
      --danger: #b42318;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--canvas);
      color: var(--ink);
      font: 15px/1.5 ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header {{
      color: #f7fbf9;
      background: var(--deep);
      border-top: 4px solid var(--amber);
      border-bottom: 1px solid #31524b;
    }}
    .header-inner, main {{ width: min(1120px, calc(100% - 32px)); margin: 0 auto; }}
    .header-inner {{
      min-height: 94px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
    }}
    .brand {{ display: flex; align-items: center; gap: 14px; min-width: 0; }}
    .brand-logo {{ width: 54px; height: 54px; padding: 7px; background: #f7fbf9; border: 1px solid #537169; border-radius: 6px; }}
    .brand-copy {{ min-width: 0; }}
    h1 {{ margin: 0; font-size: 24px; line-height: 1.15; letter-spacing: 0; }}
    .tagline {{ margin: 5px 0 0; color: #b9cbc5; font-size: 13px; }}
    nav {{ display: flex; gap: 16px; flex-wrap: wrap; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
    nav a {{ color: #d8e8e2; font-size: 13px; font-weight: 650; text-decoration: none; border-bottom: 2px solid transparent; }}
    nav a:hover {{ color: #ffffff; border-bottom-color: var(--amber); }}
    .signal-line {{ display: grid; grid-template-columns: 1.4fr 0.7fr 2.2fr 0.45fr; height: 5px; }}
    .signal-line span:nth-child(1) {{ background: var(--blue); }}
    .signal-line span:nth-child(2) {{ background: var(--amber); }}
    .signal-line span:nth-child(3) {{ background: var(--accent); }}
    .signal-line span:nth-child(4) {{ background: var(--coral); }}
    main {{ padding: 30px 0 56px; }}
    .overview {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 16px;
    }}
    h2 {{ margin: 0; font-size: 17px; letter-spacing: 0; }}
    .summary {{ margin: 4px 0 0; color: var(--muted); font-size: 13px; }}
    .bundle-state {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 32px;
      padding: 5px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: #f8fbf9;
      font-size: 13px;
      font-weight: 650;
      white-space: nowrap;
    }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; background: #8a948d; flex: 0 0 auto; }}
    .dot.ok {{ background: var(--accent); }}
    .dot.error {{ background: var(--danger); }}
    .installation {{
      position: relative;
      display: grid;
      grid-template-columns: minmax(210px, 0.72fr) minmax(0, 1.7fr);
      gap: 28px;
      margin: 0 0 20px;
      padding: 24px 26px;
      overflow: hidden;
      color: #f7fbf9;
      background: var(--deep-soft);
      border-left: 6px solid var(--amber);
      border-radius: 6px;
    }}
    .installation::after {{ content: ""; position: absolute; right: 0; top: 0; width: 10px; height: 100%; background: var(--blue); }}
    .eyebrow {{ display: block; margin-bottom: 7px; color: #f3c972; font-size: 11px; font-weight: 800; text-transform: uppercase; }}
    .installation h2 {{ font-size: 20px; }}
    .installation-role {{ margin: 5px 0 0; color: #b9cbc5; font-size: 13px; }}
    .identity-fields {{ display: grid; gap: 10px; min-width: 0; align-content: center; }}
    .identity-field {{ display: grid; grid-template-columns: 74px minmax(0, 1fr); gap: 10px; align-items: baseline; }}
    .identity-field span {{ color: #a9c1b9; font-size: 11px; font-weight: 700; text-transform: uppercase; }}
    .identity-field code {{ color: #ffffff; font-size: 12px; }}
    .identity-missing {{ color: #d7e3df; font-size: 13px; }}
    .services {{ border: 1px solid var(--line); border-radius: 7px; overflow: hidden; background: var(--surface); box-shadow: 0 10px 28px rgba(18, 49, 44, 0.08); }}
    .advisory {{
      display: grid;
      grid-template-columns: minmax(150px, 0.45fr) minmax(0, 1.55fr);
      gap: 20px;
      margin: 0 0 20px;
      padding: 16px 18px;
      border: 1px solid #e3c791;
      border-left: 4px solid var(--warning);
      border-radius: 6px;
      background: #fffaf0;
    }}
    .advisory-label {{ color: var(--warning); font-size: 12px; font-weight: 750; text-transform: uppercase; }}
    .advisory h2 {{ margin-top: 3px; }}
    .advisory p {{ margin: 0; color: #584b36; font-size: 13px; }}
    .advisory p + p {{ margin-top: 7px; }}
    .advisory code {{ color: var(--ink); }}
    .service {{
      display: grid;
      grid-template-columns: minmax(140px, 0.7fr) minmax(240px, 1.5fr) minmax(110px, 0.55fr);
      gap: 24px;
      align-items: center;
      min-height: 92px;
      padding: 18px 20px;
      border-top: 1px solid var(--line);
      border-left: 4px solid var(--accent);
    }}
    .service:first-child {{ border-top: 0; }}
    .service[data-service="safebox_web"] {{ border-left-color: var(--blue); }}
    .service[data-service="clear"] {{ border-left-color: var(--amber); }}
    .service[data-service="grove"] {{ border-left-color: var(--accent); }}
    .service[data-service="spurline"] {{ border-left-color: var(--coral); }}
    .service-name {{ margin: 0; font-size: 15px; font-weight: 700; overflow-wrap: anywhere; }}
    .kind {{ display: inline-block; margin-top: 4px; padding: 2px 5px; color: #4d5f57; background: #edf2ef; border-radius: 3px; font-size: 11px; }}
    .addresses {{ min-width: 0; }}
    .address {{ display: grid; grid-template-columns: 78px minmax(0, 1fr); gap: 8px; font-size: 13px; }}
    .address + .address {{ margin-top: 5px; }}
    .address-label {{ color: var(--muted); }}
    code {{ font: 12px/1.5 ui-monospace, SFMono-Regular, Consolas, monospace; overflow-wrap: anywhere; }}
    .service-state {{ display: flex; align-items: center; justify-content: flex-end; gap: 8px; font-size: 13px; }}
    .service-identity {{ grid-column: 1 / -1; display: grid; grid-template-columns: 78px minmax(0, 1fr) auto; gap: 8px; align-items: baseline; border-top: 1px solid var(--line); padding-top: 14px; }}
    .service-identity[hidden] {{ display: none; }}
    .identity-label, .identity-meta, .fips-label, .operator-label, .operator-meta {{ color: var(--muted); font-size: 12px; }}
    .identity-npub, .identity-fips, .operator-npub {{ min-width: 0; }}
    .identity-fips {{ grid-column: 2 / -1; }}
    .fips-field[hidden] {{ display: none; }}
    .operator-field[hidden] {{ display: none; }}
    .service-report {{ grid-column: 1 / -1; border-top: 1px solid var(--line); padding-top: 14px; }}
    .service-report summary {{ color: var(--accent); cursor: pointer; font-size: 13px; font-weight: 650; }}
    .report-grid {{ display: grid; grid-template-columns: minmax(120px, 0.35fr) minmax(0, 1fr); gap: 7px 18px; margin: 14px 0 2px; }}
    .report-grid dt {{ color: var(--muted); font-size: 12px; overflow-wrap: anywhere; }}
    .report-grid dd {{ margin: 0; font: 12px/1.5 ui-monospace, SFMono-Regular, Consolas, monospace; overflow-wrap: anywhere; }}
    .report-error {{ margin: 12px 0 0; color: var(--warning); font-size: 12px; }}
    .service[data-enabled="false"] {{ opacity: 0.58; }}
    .detail {{ margin-top: 20px; color: var(--muted); font-size: 12px; }}
    .detail span + span::before {{ content: " / "; color: #a3aaa5; }}
    @media (max-width: 700px) {{
      .header-inner {{ align-items: flex-start; flex-direction: column; gap: 14px; padding: 18px 0; }}
      .brand-logo {{ width: 48px; height: 48px; }}
      .overview {{ align-items: flex-start; flex-direction: column; gap: 12px; }}
      .installation {{ grid-template-columns: 1fr; gap: 18px; padding: 21px 20px; }}
      .identity-field {{ grid-template-columns: 1fr; gap: 2px; }}
      .advisory {{ grid-template-columns: 1fr; gap: 8px; }}
      .service {{ grid-template-columns: 1fr; gap: 12px; }}
      .service-state {{ justify-content: flex-start; }}
      .service-identity {{ grid-template-columns: 1fr; gap: 3px; }}
      .identity-fips {{ grid-column: auto; }}
      .report-grid {{ grid-template-columns: 1fr; gap: 2px; }}
      .report-grid dd + dt {{ margin-top: 7px; }}
    }}
  </style>
</head>
<body>
  <header>
    <div class="header-inner">
      <div class="brand">
        <img class="brand-logo" src="assets/mainstay-logo.svg" alt="">
        <div class="brand-copy">
          <h1>Mainstay Local</h1>
          <p class="tagline">There's no place like home.</p>
        </div>
      </div>
      <nav aria-label="API endpoints">
        <a href="identity">Identity</a>
        <a href="health">Health</a>
        <a href="registry">Registry</a>
        <a href="status">Status JSON</a>
      </nav>
    </div>
  </header>
  <div class="signal-line" aria-hidden="true"><span></span><span></span><span></span><span></span></div>
  <main>
    {installation_panel}
    <section class="overview" aria-labelledby="services-title">
      <div>
        <h2 id="services-title">Service network</h2>
        <p class="summary">{len(bundle.services)} services coordinated inside this installation</p>
      </div>
      <div class="bundle-state" aria-live="polite">
        <span class="dot" id="bundle-dot"></span>
        <span id="bundle-state">Checking services</span>
      </div>
    </section>
    {reserve_advisory}
    <div class="services">
      {service_rows}
    </div>
    <p class="detail">
      <span>Registry: {escape(bundle.name)}</span>
      <span>Control plane: port {bundle.port}</span>
      <span id="last-checked">Waiting for first check</span>
    </p>
  </main>
  <script>
    const loopbackHosts = new Set(["127.0.0.1", "localhost", "::1"]);
    document.querySelectorAll("[data-local-url]").forEach((link) => {{
      const url = new URL(link.dataset.localUrl);
      if (loopbackHosts.has(url.hostname) && !loopbackHosts.has(window.location.hostname)) {{
        url.hostname = window.location.hostname;
        link.href = url.toString();
        link.textContent = url.toString().replace(/[/]$/, "");
      }}
    }});

    async function refreshStatus() {{
      const bundleLabel = document.getElementById("bundle-state");
      const bundleDot = document.getElementById("bundle-dot");
      try {{
        const response = await fetch("status", {{ cache: "no-store" }});
        if (!response.ok) throw new Error(`HTTP ${{response.status}}`);
        const payload = await response.json();
        const results = new Map(payload.services.map((service) => [service.name, service]));
        document.querySelectorAll(".service[data-service]").forEach((row) => {{
          const result = results.get(row.dataset.service);
          if (!result) return;
          const dot = row.querySelector(".dot");
          const label = row.querySelector(".state-label");
          dot.className = `dot ${{result.ok ? "ok" : "error"}}`;
          label.textContent = result.ok ? "Available" : "Unavailable";
          row.title = result.detail || "";
          renderIdentity(row.querySelector(".service-identity"), result.homepage);
          renderHomepage(row.querySelector(".service-report"), result.homepage);
        }});
        const healthy = payload.status === "ok";
        bundleDot.className = `dot ${{healthy ? "ok" : "error"}}`;
        bundleLabel.textContent = healthy ? "All services available" : "Service attention needed";
      }} catch (error) {{
        bundleDot.className = "dot error";
        bundleLabel.textContent = "Status check failed";
      }} finally {{
        document.getElementById("last-checked").textContent =
          `Checked ${{new Date().toLocaleTimeString([], {{ hour: "2-digit", minute: "2-digit" }})}}`;
      }}
    }}

    function renderIdentity(container, homepage) {{
      const identity = homepage?.ok && homepage.report &&
        typeof homepage.report === "object" && !Array.isArray(homepage.report)
          ? homepage.report.service_identity
          : null;
      const npub = identity && typeof identity.npub === "string"
        ? identity.npub.trim()
        : "";
      if (!npub.startsWith("npub1")) {{
        container.hidden = true;
        container.querySelector(".identity-npub").textContent = "";
        container.querySelector(".identity-meta").textContent = "";
        container.querySelector(".identity-fips").textContent = "";
        for (const field of container.querySelectorAll(".fips-field")) {{
          field.hidden = true;
        }}
        for (const field of container.querySelectorAll(".operator-field")) {{
          field.hidden = true;
        }}
        return;
      }}
      container.hidden = false;
      const publicKey = container.querySelector(".identity-npub");
      publicKey.textContent = npub;
      publicKey.title = npub;
      container.querySelector(".identity-meta").textContent =
        [identity.type, identity.management, identity.state]
          .filter((value) => typeof value === "string" && value.trim())
          .join(", ");
      const fipsAddress = typeof identity.fips_ipv6_address === "string"
        ? identity.fips_ipv6_address.trim()
        : "";
      for (const field of container.querySelectorAll(".fips-field")) {{
        field.hidden = !fipsAddress;
      }}
      const fips = container.querySelector(".identity-fips");
      fips.textContent = fipsAddress;
      fips.title = fipsAddress;
      const operator = identity.operator && typeof identity.operator === "object"
        ? identity.operator
        : null;
      const operatorNpub = operator && typeof operator.npub === "string"
        ? operator.npub.trim()
        : "";
      const operatorFields = container.querySelectorAll(".operator-field");
      for (const field of operatorFields) {{
        field.hidden = !operatorNpub.startsWith("npub1");
      }}
      if (operatorNpub.startsWith("npub1")) {{
        const operatorKey = container.querySelector(".operator-npub");
        operatorKey.textContent = operatorNpub;
        operatorKey.title = operatorNpub;
        container.querySelector(".operator-meta").textContent =
          typeof operator.status === "string" ? operator.status : "";
      }}
    }}

    function renderHomepage(container, homepage) {{
      if (!homepage) {{
        container.hidden = true;
        return;
      }}
      container.hidden = false;
      const summary = container.querySelector("summary");
      const report = container.querySelector(".report-content");
      report.replaceChildren();
      if (!homepage.ok) {{
        summary.textContent = "Service report unavailable";
        const message = document.createElement("p");
        message.className = "report-error";
        message.textContent = homepage.detail || "The homepage could not be read.";
        report.append(message);
        return;
      }}

      summary.textContent = "Service report";
      const reportValue = homepage.report &&
        typeof homepage.report === "object" && !Array.isArray(homepage.report)
          ? Object.fromEntries(
              Object.entries(homepage.report).filter(
                ([name]) => name !== "service_identity"
              )
            )
          : homepage.report;
      const fields = flattenReport(reportValue);
      if (!fields.length) {{
        container.hidden = true;
        return;
      }}
      const list = document.createElement("dl");
      list.className = "report-grid";
      fields.forEach(([name, value]) => {{
        const term = document.createElement("dt");
        const description = document.createElement("dd");
        term.textContent = name;
        description.textContent = formatReportValue(value);
        list.append(term, description);
      }});
      report.append(list);
    }}

    function flattenReport(value, prefix = "") {{
      if (value && typeof value === "object" && !Array.isArray(value)) {{
        return Object.entries(value).flatMap(([key, child]) => {{
          const name = prefix ? `${{prefix}}.${{key}}` : key;
          if (child && typeof child === "object" && !Array.isArray(child)) {{
            return flattenReport(child, name);
          }}
          return [[name, child]];
        }});
      }}
      return [[prefix || "response", value]];
    }}

    function formatReportValue(value) {{
      if (value === null) return "null";
      if (Array.isArray(value)) return value.map(formatReportValue).join(", ");
      if (typeof value === "object") return JSON.stringify(value);
      return String(value);
    }}

    refreshStatus();
    window.setInterval(refreshStatus, 15000);
  </script>
</body>
</html>
"""


def _render_service_row(name: str, endpoint: ServiceEndpoint) -> str:
    endpoint_rows = "\n".join(
        _render_endpoint_address(address.scope, address.url)
        for address in endpoint.endpoints
    )

    initial_state = "Disabled" if not endpoint.enabled else "Checking"
    return f"""<article class="service" data-service="{escape(name)}" data-enabled="{str(endpoint.enabled).lower()}">
        <div>
          <p class="service-name">{escape(name.replace("_", " "))}</p>
          <span class="kind">{escape(endpoint.kind)}</span>
        </div>
        <div class="addresses">
          {endpoint_rows}
        </div>
        <div class="service-state"><span class="dot"></span><span class="state-label">{initial_state}</span></div>
        <div class="service-identity" hidden>
          <span class="identity-label">Identity</span>
          <code class="identity-npub"></code>
          <span class="identity-meta"></span>
          <span class="fips-label fips-field" hidden>FIPS IPv6</span>
          <code class="identity-fips fips-field" hidden></code>
          <span class="operator-label operator-field" hidden>Operator</span>
          <code class="operator-npub operator-field" hidden></code>
          <span class="operator-meta operator-field" hidden></span>
        </div>
        <details class="service-report" hidden>
          <summary>Service report</summary>
          <div class="report-content"></div>
        </details>
      </article>"""


def installation_identity(installation_npub: str | None) -> dict[str, Any] | None:
    if not installation_npub:
        return None
    try:
        fips_address = fips_ipv6_address(installation_npub)
    except (TypeError, ValueError):
        fips_address = None
    return {
        "npub": installation_npub,
        "fips_ipv6_address": fips_address,
        "type": "mainstay-installation",
        "management": "self-managed",
        "state": "active",
        "role": "installation and control plane",
    }


def _render_installation_panel(
    bundle: BundleConfig,
    *,
    installation_npub: str | None,
) -> str:
    identity = installation_identity(installation_npub)
    if identity is None:
        fields = '<p class="identity-missing">Installation identity unavailable</p>'
    else:
        fips_address = identity.get("fips_ipv6_address") or "Unavailable"
        fields = f"""<div class="identity-field">
          <span>Identity</span>
          <code>{escape(str(identity["npub"]))}</code>
        </div>
        <div class="identity-field">
          <span>FIPS IPv6</span>
          <code>{escape(str(fips_address))}</code>
        </div>"""
    return f"""<section class="installation" aria-labelledby="installation-title">
      <div>
        <span class="eyebrow">Mainstay installation</span>
        <h2 id="installation-title">{escape(bundle.name)}</h2>
        <p class="installation-role">Installation identity and local control plane</p>
      </div>
      <div class="identity-fields">{fields}</div>
    </section>"""


def _render_reserve_advisory(bundle: BundleConfig) -> str:
    safebox_web = bundle.services.get("safebox_web")
    if safebox_web is None or not safebox_web.enabled:
        return ""
    amount = bundle.service_acorn_reserve_sats
    command = (
        "docker compose stop service-acorn-worker && "
        "docker compose run --rm --no-deps service-acorn-worker "
        f"python -m app.service_acorn_worker fund {amount}"
    )
    return f"""<section class="advisory" aria-labelledby="reserve-title">
      <div>
        <span class="advisory-label">Required bootstrap step</span>
        <h2 id="reserve-title">Confirm Lightning fee reserve</h2>
      </div>
      <div>
        <p>The service Acorn needs at least {amount} sats of operator-funded reserve to cover mint input fees while delivering Lightning-address payments. A healthy worker can create invoices before this reserve exists.</p>
        <p>Mainstay does not yet measure the reserve automatically. Check it with <code>poetry run mainstay-local reserve balance</code>, fund it after first startup, and replenish it as fees consume it.</p>
        <p><code>{escape(command)}</code></p>
      </div>
    </section>"""


def _render_endpoint_address(scope: str, url: str) -> str:
    escaped_url = escape(url)
    scheme = urlsplit(url).scheme
    if scope in {"local", "external"} and scheme in {"http", "https"}:
        data_attribute = (
            f' data-local-url="{escaped_url}"' if scope == "local" else ""
        )
        markup = f'<a href="{escaped_url}"{data_attribute}>{escaped_url}</a>'
    else:
        markup = f"<code>{escaped_url}</code>"
    return (
        '<div class="address">'
        f'<span class="address-label">{escape(scope.title())}</span>'
        f"<span>{markup}</span></div>"
    )


def render_service_context(
    bundle: BundleConfig,
    *,
    installation_npub: str | None,
    timeout: float = 1.0,
) -> dict[str, Any]:
    """Return public identities and routes supplied by this installation."""

    services: list[dict[str, Any]] = []
    grove = bundle.services.get("grove")
    if installation_npub and grove is not None and grove.enabled:
        homepage = (
            inspect_homepage(grove.homepage_url, timeout=timeout)
            if grove.homepage_url
            else None
        )
        report = homepage.report if homepage is not None and homepage.ok else None
        identity = report.get("service_identity") if isinstance(report, dict) else None
        service_npub = identity.get("npub") if isinstance(identity, dict) else None
        if isinstance(service_npub, str) and service_npub.strip():
            endpoints = []
            for address in grove.endpoints:
                parsed = urlsplit(address.url)
                if parsed.scheme not in {"http", "https"}:
                    continue
                endpoints.append(
                    {
                        "endpoint_id": (
                            f"mainstay-{grove.name}-{address.scope}-{address.purpose}"
                        ),
                        "scope": address.scope,
                        "transport": parsed.scheme,
                        "locator": {"url": address.url},
                        "capabilities": list(GROVE_CAPABILITIES),
                        "priority": address.priority,
                    }
                )
            services.append(
                {
                    "name": grove.name,
                    "service_type": grove.kind,
                    "service_npub": service_npub.strip(),
                    "endpoints": endpoints,
                }
            )
    return {
        "type": "mainstay-service-context",
        "version": 1,
        "context_npub": installation_npub,
        "fips_ipv6_address": (
            installation_identity(installation_npub) or {}
        ).get("fips_ipv6_address"),
        "services": services,
    }


def serve(
    bundle: BundleConfig,
    *,
    host: str,
    port: int,
    installation_npub: str | None = None,
) -> None:
    handler = _handler_for(bundle, installation_npub=installation_npub)
    server = ThreadingHTTPServer((host, port), handler)
    print(f"mainstay-local listening on http://{host}:{port}")
    server.serve_forever()


def _handler_for(
    bundle: BundleConfig,
    *,
    installation_npub: str | None = None,
) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:
            if self.path == "/":
                self._send_text(
                    render_dashboard(
                        bundle,
                        installation_npub=installation_npub,
                    ),
                    content_type="text/html; charset=utf-8",
                )
                return
            if self.path == "/assets/mainstay-logo.svg":
                self._send_bytes(
                    MAINSTAY_LOGO_SVG,
                    content_type="image/svg+xml; charset=utf-8",
                )
                return
            if self.path == "/identity":
                self._send_json(
                    {
                        "name": bundle.name,
                        "service_identity": installation_identity(
                            installation_npub
                        ),
                    }
                )
                return
            if self.path == "/health":
                self._send_json(
                    {
                        "status": "ok",
                        "service": "mainstay-local",
                        "version": __version__,
                    }
                )
                return
            if self.path == "/registry":
                self._send_json(bundle.to_dict())
                return
            if self.path == "/context":
                self._send_json(
                    render_service_context(
                        bundle,
                        installation_npub=installation_npub,
                    )
                )
                return
            if self.path == "/status":
                results = check_bundle(bundle, timeout=1.0)
                self._send_json(
                    {
                        "status": (
                            "ok" if all(result.ok for result in results) else "degraded"
                        ),
                        "services": [
                            {
                                "name": result.name,
                                "target": result.target,
                                "ok": result.ok,
                                "detail": result.detail,
                                "homepage": (
                                    result.homepage.to_dict()
                                    if result.homepage is not None
                                    else None
                                ),
                            }
                            for result in results
                        ],
                    }
                )
                return
            self.send_error(404)

        def log_message(self, format: str, *args: Any) -> None:
            return

        def _send_json(self, payload: dict[str, Any]) -> None:
            body = json.dumps(payload, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_text(self, text: str, *, content_type: str) -> None:
            self._send_bytes(text.encode("utf-8"), content_type=content_type)

        def _send_bytes(self, body: bytes, *, content_type: str) -> None:
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


MAINSTAY_LOGO_SVG = b"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512" role="img" aria-label="Mainstay logo">
  <path fill="#2f66d8" d="M64 205 256 66l192 139v73l-48-35v135h-48V208l-96-70-96 70v170h-48V243l-48 35z"/>
  <path fill="#173b78" d="M64 394h168V198l24-24 24 24v196h168v52H64z"/>
  <path fill="#e4a53a" d="M280 246h96l38 34-38 34h-96z"/>
</svg>"""
