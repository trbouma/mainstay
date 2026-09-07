# The self-contained dashboard keeps its CSS and JavaScript readable in-place.
# ruff: noqa: E501

from __future__ import annotations

import json
from html import escape
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import urlsplit

from .registry import BundleConfig, ServiceEndpoint
from .status import check_bundle, inspect_homepage

GROVE_CAPABILITIES = ("blossom.read", "blossom.write", "blossom.delete")


def render_dashboard(bundle: BundleConfig) -> str:
    service_rows = "\n".join(
        _render_service_row(name, endpoint)
        for name, endpoint in bundle.services.items()
    )
    reserve_advisory = _render_reserve_advisory(bundle)
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
      --ink: #17211c;
      --muted: #667169;
      --line: #d9dfdb;
      --surface: #ffffff;
      --canvas: #f3f6f4;
      --accent: #087f5b;
      --accent-soft: #dff3eb;
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
      background: var(--surface);
      border-bottom: 1px solid var(--line);
    }}
    .header-inner, main {{ width: min(1080px, calc(100% - 32px)); margin: 0 auto; }}
    .header-inner {{
      min-height: 76px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 24px;
    }}
    .brand {{ min-width: 0; }}
    h1 {{ margin: 0; font-size: 20px; line-height: 1.2; letter-spacing: 0; }}
    .tagline {{ margin: 4px 0 0; color: var(--muted); font-size: 13px; }}
    nav {{ display: flex; gap: 16px; flex-wrap: wrap; }}
    a {{ color: var(--accent); text-underline-offset: 3px; }}
    nav a {{ font-size: 13px; font-weight: 650; text-decoration: none; }}
    main {{ padding: 36px 0 56px; }}
    .overview {{
      display: flex;
      align-items: end;
      justify-content: space-between;
      gap: 24px;
      margin-bottom: 18px;
    }}
    h2 {{ margin: 0; font-size: 16px; letter-spacing: 0; }}
    .summary {{ margin: 4px 0 0; color: var(--muted); font-size: 13px; }}
    .bundle-state {{
      display: inline-flex;
      align-items: center;
      gap: 8px;
      min-height: 32px;
      padding: 5px 10px;
      border: 1px solid var(--line);
      border-radius: 6px;
      background: var(--surface);
      font-size: 13px;
      font-weight: 650;
      white-space: nowrap;
    }}
    .dot {{ width: 8px; height: 8px; border-radius: 50%; background: #8a948d; flex: 0 0 auto; }}
    .dot.ok {{ background: var(--accent); }}
    .dot.error {{ background: var(--danger); }}
    .services {{ border: 1px solid var(--line); border-radius: 8px; overflow: hidden; background: var(--surface); }}
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
    }}
    .service:first-child {{ border-top: 0; }}
    .service-name {{ margin: 0; font-size: 15px; font-weight: 700; overflow-wrap: anywhere; }}
    .kind {{ color: var(--muted); font-size: 12px; }}
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
      .overview {{ align-items: flex-start; flex-direction: column; gap: 12px; }}
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
        <h1>Mainstay Local</h1>
        <p class="tagline">There's no place like home.</p>
      </div>
      <nav aria-label="API endpoints">
        <a href="/health">Health</a>
        <a href="/registry">Registry</a>
        <a href="/status">Status JSON</a>
      </nav>
    </div>
  </header>
  <main>
    <section class="overview" aria-labelledby="services-title">
      <div>
        <h2 id="services-title">Local services</h2>
        <p class="summary">{len(bundle.services)} registered services</p>
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
        const response = await fetch("/status", {{ cache: "no-store" }});
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
        <p>Mainstay does not yet measure the reserve automatically. Fund it after first startup and replenish it as fees consume it.</p>
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
                    render_dashboard(bundle),
                    content_type="text/html; charset=utf-8",
                )
                return
            if self.path == "/health":
                self._send_json({"status": "ok"})
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
            body = text.encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler
