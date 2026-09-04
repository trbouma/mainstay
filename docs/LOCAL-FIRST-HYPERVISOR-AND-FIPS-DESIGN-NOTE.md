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

The current prototype lives in the Safebox Web repo:

```text
safebox-web/deploy/local-first/
```

`mainstay-local` should eventually absorb the orchestration model, not the
Safebox Web application code.

Mainstay is absorbing that model incrementally. Spurline and Grove are the
first services in the Mainstay Compose project. Their container ports are
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
checks service health, and can hand the generated env file to the Safebox Web
local-first Compose prototype.

## Endpoint Model

The central abstraction `mainstay-local` needs is an endpoint registry. It should
separate:

- service identity;
- local runtime address;
- advertised address;
- protocol kind;
- transport substrate; and
- authorization policy.

Sketch:

```yaml
services:
  safebox_web:
    kind: app
    local_url: http://safebox-web:8000
    advertised_url: http://127.0.0.1:8000

  clear:
    kind: clear-mint
    local_url: http://clear:3339
    advertised_url: http://clear:3339
    fips_npub: npub...
    fips_port: 3339

  grove:
    kind: blossom
    local_url: http://grove:8000
    advertised_url: http://grove:8000
    fips_npub: npub...
    fips_port: 8000

  spurline:
    kind: nostr-relay
    local_url: ws://spurline:8080
    advertised_url: ws://spurline:8080
    fips_npub: npub...
    fips_port: 8080
```

Safebox Web currently accepts URLs through environment variables.
`mainstay-local` can generate those variables from its endpoint registry at
startup. That gives Mainstay room to move from Docker DNS to loopback, LAN,
Tailscale, `.fips`, FIPS-derived IPv6, or jail-local addresses without
rewriting Safebox Web routes.

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
| Internal vs advertised addresses | Add explicit support where one URL is used both for service calls and externally embedded references |
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

1. Continue moving the proven Docker services from
   `safebox-web/deploy/local-first` into Mainstay one at a time; Spurline is the
   first managed service, followed by Grove.
2. Add a `mainstay-local` endpoint-registry document or schema.
3. Inventory Safebox Web locations where one URL currently does double duty as
   both internal endpoint and advertised endpoint.
4. Add missing Safebox Web configuration seams before introducing Mainstay
   runtime code.
5. Build a minimal `mainstay-local config` command that emits a Safebox Web env
   file from the endpoint registry.
6. Build `mainstay-local status` against existing `/health` endpoints.
7. After Docker smoke tests pass, sketch the FreeBSD jail process graph using
   the same endpoint registry.
8. Add FIPS endpoint fields to the registry and test the HTTP/WebSocket services
   over `fips0` before considering native FIPS APIs.
