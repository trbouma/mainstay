# Local-First Hypervisor and FIPS Design Note

## Purpose

`mainstay-local` is the local-first hypervisor app that should live in the
Mainstay repo. Safebox Web can prove the user-facing workflows and
configuration seams, but `mainstay-local` should become the application that
starts, observes, configures, and migrates the local infrastructure bundle.

The first executable step is still a Docker network: start Safebox Web, Clear,
Grove, and Spurline as one local service graph, with Safebox Acorn embedded as
the protocol kernel inside Safebox Web. The longer-term target is FreeBSD jails
and FIPS-based reachability rather than DNS-bound service identity.

This note records how `mainstay-local` should use that first Docker prototype
to drive the changes needed in Safebox Web.

## Product Boundary

```text
mainstay-local
    -> owns local-first setup, service graph, health, backup, migration,
       endpoint identity, and FIPS binding

Safebox Web
    -> owns current web workflows, sessions, records, funds, NIP-05, LNURL,
       Clear receive UX, and service-Acorn worker

Safebox Acorn
    -> owns keys, records, mints, relays, Blossom, Clear proof state, recovery,
       and protocol invariants

Clear / Grove / Spurline
    -> own local mint, blob, and relay infrastructure
```

`mainstay-local` should not fork Safebox Web just to change deployment
defaults. Its job is to reveal which assumptions in Safebox Web need to become
configurable, then consume those settings from a higher-level local bundle
model.

## First Docker Shape

The initial `mainstay-local` app can treat Docker Compose as the execution
engine:

```text
mainstay-local up
    -> create Docker network
    -> start clear
    -> start grove
    -> start spurline
    -> start safebox-web
    -> start service-acorn-worker
    -> show health and public entrypoint
```

Only Safebox Web should be published by default. Clear, Grove, and Spurline
should be private infrastructure unless the operator explicitly enables debug
ports or external service origins.

The integration prototype now lives in the Mainstay repo:

```text
mainstay/docker-compose.yaml
```

Safebox Web and its service-Acorn worker are an explicit Compose profile. The
profile is disabled by default so Mainstay can manage local infrastructure
without taking over or conflicting with an independently deployed Safebox Web
instance. Mainstay owns the orchestration model, not the Safebox Web
application code.

Mainstay is absorbing that model incrementally. Spurline, Grove, and Clear are
the first services in the Mainstay Compose project. Their container ports are
private by default, their data volumes are scoped to the Compose project, and
an optional overlay publishes loopback diagnostic ports. Existing standalone
deployments are not joined, renamed, or modified.

The first prototype lives in `app/` and is intentionally small:

```text
python -m app init
python -m app config
python -m app status
python -m app up
```

It creates a JSON endpoint registry, renders Safebox Web environment settings,
checks service health, and can enable the Safebox Web profile when the endpoint
registry deliberately marks that application as enabled.

## Independent Safebox Web Safety

Safebox Web retains its standalone `docker-compose.yaml` and deployment
settings. Moving the integration profile into Mainstay does not alter that
file, its Compose project, its containers, or its persistent volume.

The Mainstay integration uses Mainstay-scoped container and volume names. A
default `docker compose up` in Mainstay starts the Mainstay control
plane, its managed infrastructure, and a Mainstay-owned Safebox Web instance.
Safebox publishes host port `8888` by default so trusted LAN or VPN clients can
reach it over explicitly enabled local HTTP and so it can coexist with a
standalone instance on `8000`. Host-port conflicts remain visible and fail
closed at container startup; Mainstay does not replace a running standalone
container or reuse its data volume. The singleton service-Acorn worker runs as
a separate process in the default bundle and retains its identity in the
Mainstay-scoped Safebox volume.

## Endpoint Model

The detailed scope and transport rules are defined in
[Address Spaces, Endpoint Scopes, and FIPS](ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md).

The central abstraction `mainstay-local` needs is an endpoint registry. It should
separate:

- service identity;
- scoped internal, local, and external addresses;
- protocol kind;
- transport substrate; and
- authorization policy.

Sketch:

```yaml
services:
  safebox_web:
    kind: app
    endpoints:
      - scope: internal
        purpose: web
        url: http://safebox-web:8000
        priority: 10
      - scope: local
        purpose: web
        url: http://127.0.0.1:8888
        priority: 20
    homepage_url: http://safebox-web:8000/

  clear:
    kind: clear-mint
    endpoints:
      - scope: internal
        purpose: mint
        url: http://clear:3339
        priority: 10
    homepage_url: http://clear:3339/
    fips_npub: npub...
    fips_port: 3339

  lightning_mint:
    kind: cashu-lightning-mint
    endpoints:
      - scope: external
        purpose: mint
        url: https://mint.safebox.dev
        priority: 10

  grove:
    kind: blossom
    endpoints:
      - scope: internal
        purpose: blossom
        url: http://grove:8000
        priority: 10
    homepage_url: http://grove:8000/
    fips_npub: npub...
    fips_port: 8000

  spurline:
    kind: nostr-relay
    endpoints:
      - scope: internal
        purpose: relay
        url: ws://spurline:8080
        priority: 10
    homepage_url: http://spurline:8080/
    fips_npub: npub...
    fips_port: 8080
```

Safebox Web currently accepts URLs through environment variables.
`mainstay-local` can generate those variables from its endpoint registry at
startup. That gives Mainstay room to move from Docker DNS to loopback, LAN,
Tailscale, `.fips`, FIPS-derived IPv6, or jail-local addresses without
rewriting Safebox Web routes.

Clear and Lightning-backed Cashu mints are separate service classes. Mainstay
provides Clear at the internal `http://clear:3339` endpoint for Clear balances
and transfers. A newly created Acorn instead uses the external
`https://mint.safebox.dev` Cashu mint as its home mint. Mainstay must not put
the Clear endpoint into `SAFEBOX_DEFAULT_HOME_MINT` or
`SAFEBOX_SERVICE_ACORN_HOME_MINT`.

Each endpoint declares a reachability scope. `internal` is private to the
Mainstay runtime, `local` is deliberately reachable on a trusted host, LAN, or
VPN, and `external` is intended for access beyond that local environment. The
dashboard renders only configured scopes. Clear, Grove, and Spurline begin with
internal endpoints only. Safebox always receives their internal endpoints;
service-generated routing hints may prefer an explicitly configured external
or local endpoint while retaining the internal endpoint as a fallback.
When more than one endpoint has the same scope and purpose, the lowest
`priority` value is selected first.

Endpoint URLs are locations, not durable service identities. In particular,
Clear Mint Notes retain their complete keyset ID as the stable CMU identity;
an endpoint carried in a token remains a routing hint. The registry accepts
legacy `local_url` and `advertised_url` fields during migration, mapping them to
`internal` and `local` scopes respectively, but newly generated registries emit
only scoped endpoints.

The registry also gives the Mainstay dashboard an explicit HTTP homepage to
inspect. For a running service, the control plane requests JSON when available
and exposes a bounded, sanitized summary. HTML homepages contribute only title
and description metadata; Mainstay does not embed service-supplied markup.

In the Docker phase, `spurline` is a network-scoped resolution label, not a
durable service identity. Mainstay's logical service key remains stable while
the runtime URL may later become a jail address, LAN address, FIPS-derived IPv6
address, or gateway endpoint. Health checks executed inside the control-plane
container must use the runtime namespace (`http://spurline:8080/health`), not a
host-loopback diagnostic URL.

Grove follows the same rule at `http://grove:8000`. During the private Docker
phase, this is both its runtime origin and its BUD-11 authorization server name.
Publishing `127.0.0.1:8001` through the debug overlay provides host diagnostics
only; it does not create another advertised Blossom identity. A future gateway
must update Grove's advertised origin and authorization name together.

Clear runs at `http://clear:3339` inside the Docker phase. This first managed
profile creates a new root-bootstrap mint from operator-supplied secrets and a
project-scoped database volume. Mainstay must never silently regenerate
`CLEAR_MASTER_SECRET`, change `CLEAR_ROOT_AUTHORITY_NPUB`, or attach an existing
database to different identity inputs. The optional host debug port is not a
new canonical mint URL and must not be encoded into Mint Notes.

Process health is not commissioning. The current Clear implementation does not
yet provide the accepted root verification state machine or treasury readiness
gate. Mainstay may report the process as available, but must not label the mint
commissioned or enable treasury operations. Connecting to an established mint
will be a separate external-service registry mode rather than another startup
path for this managed container.

## FIPS Direction

FIPS should enter `mainstay-local` as infrastructure before it enters Safebox
Web as an application protocol.

The staged path should be:

1. Prove the Docker-local service graph.
2. Introduce the Mainstay endpoint registry while still emitting ordinary URLs.
3. Run the same services behind stable LAN or loopback origins.
4. Add a host-level FIPS node and expose selected services over `fips0` IPv6 or
   FIPS gateway port forwards.
5. Add FIPS npubs to the endpoint registry and operator UI.
6. Teach Safebox Web and Acorn to preserve FIPS endpoint metadata where URLs
   are currently the only persisted or advertised location.
7. Consider native FIPS APIs for narrow flows only after reliability, framing,
   and authorization requirements are explicit.

The first FIPS pass should keep ordinary HTTP and WebSocket protocols. Clear,
Grove, Spurline, and Safebox Web already have useful HTTP/WebSocket boundaries;
FIPS can replace the addressing and reachability substrate underneath them.

Native FIPS is a later step. Its current shape is datagram-oriented, while the
Safebox family currently relies on reliable request/response and WebSocket
semantics.

## Changes Mainstay Should Drive In Safebox Web

`mainstay-local` should use the local-first prototype to identify and
prioritize these Safebox Web changes:

| Need | Safebox Web change |
| --- | --- |
| Local-first defaults | Keep all relay, mint, Blossom, Clear, and provider-worker endpoints configurable by environment |
| Endpoint scopes | Keep internal service calls separate from deliberately configured local and external routes |
| FIPS metadata | Allow endpoint records to carry FIPS npubs and ports beside URLs |
| Internet independence | Make external conveniences disable cleanly, including fiat rates and public Bitcoin lookups |
| Operator-generated config | Accept a generated config bundle or env file without product-code changes |
| Health reporting | Expose small, machine-readable health and readiness checks that distinguish app, relay, mint, blob, database, and worker state |
| Protocol boundary | Keep Safebox Web invoking Acorn instead of reimplementing FIPS, relay, mint, or blob logic |

The key principle is that Safebox Web should become easier to configure, not
more responsible for orchestration.

## Mainstay-Local Responsibilities

`mainstay-local` should eventually own:

- choosing a local profile;
- generating required secrets;
- creating and starting the service graph;
- showing health and readiness state;
- managing persistent data locations;
- backing up and restoring component volumes or jail datasets;
- generating Safebox Web environment settings;
- tracking local, advertised, and FIPS endpoints;
- binding services to FIPS identities;
- applying default-deny exposure policy;
- migrating from Docker to FreeBSD jails; and
- explaining which services are local, mesh-reachable, or externally published.

This is why `mainstay-local` is the natural future app. It can be the user's
control plane for continuity without turning Safebox Web into a deployment
dashboard. Safebox Web, Stroma, and future apps should appear as apps managed by
the local runtime rather than as owners of the runtime.

## FreeBSD Jail Trajectory

The jail model should follow the same service graph:

```text
jail: safebox-web
jail: clear
jail: grove
jail: spurline
host: fips
host or jail: reverse proxy / gateway
```

Each service should get a distinct persistent dataset. The Docker volumes from
the prototype should map cleanly to those datasets:

| Docker volume | Jail/ZFS destination |
| --- | --- |
| `safebox-web-data` | Safebox Web database and service-Acorn state |
| `clear-data` | Clear mint database and root wallet |
| `grove-data` | Grove blob store and metadata |
| `spurline-data` | Spurline event store |

The open design decision is whether each service receives its own FIPS identity
or whether a host-level FIPS identity fronts several local ports. The latter is
simpler operationally; the former gives cleaner service identity and
authorization boundaries.

## Open Questions

- What is the minimal `mainstay-local` UI: terminal command, local web
  dashboard, or both?
- Should `mainstay-local` generate only `.env` and Compose files at first, or
  invoke Docker directly?
- Which Safebox Web URLs are persisted into Acorn records, tokens, NIP-05
  responses, Clear payment requests, or QR payloads?
- Where should FIPS npubs be stored so they survive Docker-to-jail migration?
- Does each infrastructure service need a distinct FIPS identity?
- What is the authorization model for services reachable from arbitrary mesh
  nodes?
- Which health checks are readiness gates and which are diagnostics only?
- When `mainstay-local` controls a local bundle, should Safebox Web still expose
  onboarding controls for changing relay and mint manually?

## Next Steps

1. Smoke-test the opt-in Safebox Web profile against Mainstay-managed Spurline,
   Grove, and Clear without changing the standalone deployment.
2. Extend the scoped endpoint registry with authenticated keyset and FIPS discovery.
3. Inventory Safebox Web locations where one URL currently does double duty as
   both an internal endpoint and a local or external routing hint.
4. Add missing Safebox Web configuration seams before introducing Mainstay
   runtime code.
5. Build a minimal `mainstay-local config` command that emits a Safebox Web env
   file from the endpoint registry.
6. Build `mainstay-local status` against existing `/health` endpoints.
7. After Docker smoke tests pass, sketch the FreeBSD jail process graph using
   the same endpoint registry.
8. Add FIPS endpoint fields to the registry and test the HTTP/WebSocket services
   over `fips0` before considering native FIPS APIs.
