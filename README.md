# Mainstay

Mainstay is a unified local-first application that keeps essential information
and value available and usable when conditions change. It brings Safebox,
Acorn, Stroma, Grove, Spurline, and Clear into one coherent product family.

Mainstay is the application. Lockbox is the appliance. There's no place like
home.

## Identity Outlives Location

Mainstay treats identity as durable and availability as an operating objective.
A service remains the same service when it moves from a Docker name to a LAN
address, public HTTPS endpoint, VPN route, FreeBSD jail, or future FIPS path.
Likewise, a wallet `npub`, Clear keyset ID, or Grove content hash does not
become a different identifier merely because the route used to reach it has
changed.

This is a digital-resilience capability, not only a configuration convenience.
DNS and public IP connectivity can remain useful routes without becoming the
root of identity or a mandatory condition for local availability. Mainstay can
select a route appropriate to the current context, replace that route as the
topology changes, and preserve the identity that users and services already
trust. See [Invariant Identity and Dynamic Resolution](docs/INVARIANT-IDENTITY-AND-DYNAMIC-RESOLUTION.md).

## Documentation

Start with the [first-time start guide](website/getting-started.md) for either
a quick testing deployment or a planned production initialization.

Design notes:

- [Invariant Identity and Dynamic Resolution](docs/INVARIANT-IDENTITY-AND-DYNAMIC-RESOLUTION.md)
- [Mainstay House Style and Family Audit](docs/MAINSTAY-HOUSE-STYLE.md)
- [Product-Family Localization](docs/LOCALIZATION-DESIGN-NOTE.md)
- [Ecosystem Responsibility Boundaries and Iterative Development](docs/ECOSYSTEM-RESPONSIBILITY-BOUNDARIES-AND-ITERATION.md)
- [White-Label Branding and Experience Profiles](docs/WHITE-LABEL-BRANDING-DESIGN-NOTE.md)
- [Mainstay Instance Lifecycle and Recovery](docs/MAINSTAY-INSTANCE-LIFECYCLE.md)
- [Clerk and Treasury Functions](docs/CLERK-AND-TREASURY-FUNCTIONS.md)
- [mainstay-local Hypervisor and FIPS](docs/LOCAL-FIRST-HYPERVISOR-AND-FIPS-DESIGN-NOTE.md)
- [Address Spaces, Endpoint Scopes, and FIPS](docs/ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md)
- [Identity, Resolution, and Event-Native Services](docs/IDENTITY-RESOLUTION-AND-EVENT-NATIVE-SERVICES.md)
- [Service Identity and Operator Attestation](docs/SERVICE-IDENTITY-AND-OPERATOR-ATTESTATION-DESIGN-NOTE.md)
- [Local Clear Transactions](docs/LOCAL-CLEAR-TRANSACTIONS-DESIGN-NOTE.md)
- [Clear Transfer Routing and Reachability](docs/CLEAR-TRANSFER-ROUTING-AND-REACHABILITY.md)
- [Clear Transfer Scope, Acceptance, and Authority](docs/CLEAR-TRANSFER-SCOPE-ACCEPTANCE-AND-AUTHORITY.md)
- [Mainstay Clear Context Wrapper](docs/MAINSTAY-CLEAR-CONTEXT-WRAPPER.md)
- [Mainstay Grove Context Integration](docs/MAINSTAY-GROVE-CONTEXT-INTEGRATION.md)
- [Mainstay Continuity Coordinator](docs/MAINSTAY-CONTINUITY-COORDINATOR-DESIGN-NOTE.md)

## Prototype App

The first `mainstay-local` prototype lives in `app/`. Install the local
development environment with Poetry:

```bash
poetry install --with dev,docs
```

Then run the CLI from this checkout:

```bash
poetry run mainstay-local init
poetry run mainstay-local config
poetry run mainstay-local status
```

It starts as a thin endpoint registry and lifecycle wrapper. The Mainstay
Compose project's current default set is Spurline, Grove, Clear, and Safebox
Web. The dashboard checks each enabled service and, when it is
running, shows a bounded report from its internal homepage. Registry endpoints
are scoped as `internal`, `local`, or `external`; Safebox dependencies use
internal endpoints even when a service also publishes another route.

The dashboard supports English, French, Spanish, Portuguese, German, Italian,
Simplified Chinese and Arabic, including right-to-left layout. Select a
language in the header or use a bookmarkable `?lang=` query; an unqualified
first visit follows the browser's supported `Accept-Language` preference.

Commission the managed Clear service under this Mainstay installation after
the updated Clear image is running:

```bash
./init-env.sh
poetry run mainstay-local service commission clear
poetry run mainstay-local service show clear
poetry run mainstay-local service verify clear
```

The host-side command signs with `MAINSTAY_INSTALLATION_NSEC`; that key is not
injected into Clear or the long-running Mainstay container. Clear independently
verifies and stores the public evidence, then publishes it to internal
Spurline. Use `--no-publish` only for an intentionally offline commissioning.

Run the local control-plane HTTP surface directly:

```bash
poetry run mainstay-local serve --host 127.0.0.1 --port 8788
```

Then open:

```text
http://127.0.0.1:8788/health
http://127.0.0.1:8788/registry
http://127.0.0.1:8788/status
```

Run the tests and linter:

```bash
poetry run pytest
poetry run ruff check .
```

## Run with Docker

> **One deployment directory per instance:** Every Mainstay instance must run
> from its own dedicated checkout or deployment directory. That directory owns
> the instance's `.env`, Compose lifecycle, generated installation identity,
> and teardown authority. Never run multiple instances from one directory or
> share one `.env` between deployment directories.
> Give each directory a unique `COMPOSE_PROJECT_NAME`; the installer prompts
> for and persists it so Compose containers, networks, and named volumes cannot
> collide with another Mainstay deployment on the same host.

For a first installation, run the interactive operator wizard:

```bash
./install-mainstay.sh
```

It prompts for a human-facing instance name, a unique Compose project name, a
parent data directory, the host bind addresses and ports for the dashboard and
Safebox Web, and the external Lightning mint used by new and service Acorns. It
also confirms the
external inbox relay advertised by NIP-05 addresses, which defaults to
`wss://spurline.safebox.dev` and may explicitly be disabled. The mint defaults
to `https://mint.safebox.dev` and must use HTTPS. A new instance
named `mainstay-testlab` with parent `/mnt/bitcoin/mainstay` uses the dedicated
root `/mnt/bitcoin/mainstay/mainstay-testlab`. Enter `abort`, `quit`, or `q` at
any prompt to stop before configuration is written. Existing `.env` values are
displayed as defaults; otherwise the shipped defaults are used. Before the
final review it performs read-only checks for Docker, Compose, OpenSSL, a
conflicting Compose namespace, data-root writability, and occupied host ports.
Every running instance on one host needs its own `MAINSTAY_LOCAL_PORT` and
`MAINSTAY_SAFEBOX_PORT`. Installation, startup, refresh, and recovery report
the container and Compose project that already owns a selected port and stop
before starting a partial service set. To resolve a conflict, choose unused
ports in that instance's `.env` and run `./start-mainstay.sh --no-build`.
`MAINSTAY_INSTANCE_NAME` controls the dashboard label independently of the
Docker namespace, so a display name such as `Cedar Resort` can use a technical
Compose project name such as `cedar-resort-prod`.
The final review defaults to not writing anything.
It also marks the operator-funded service-Acorn fee reserve as a required
post-start action. The installer does not transfer funds automatically and
prints the stop, fund, restart, and balance-check commands before it exits.

Mainstay enables Safebox Web's informational currency-rate cache by default.
The singleton service Acorn worker fetches public rates hourly while web
requests read only the shared last-known-good cache. Set
`SAFEBOX_CURRENCY_RATES_ENABLED=false` to disable this external dependency.

For routine starts after `.env` exists, validate Compose, start the bundle, and
wait for readiness with:

```bash
./start-mainstay.sh
docker compose ps
curl http://127.0.0.1:8788/health
```

To choose where persistent service data lives, set the root on the first
initialization:

```bash
./start-mainstay.sh --data-root "$HOME/mainstay-local-data"
```

This records the absolute root in `.env` and creates `mainstay-control`,
`safebox-web`, `spurline`, `grove`, and `clear` subdirectories beneath it.
Compose uses those directories as bind mounts and runs the data-writing
processes with the initializing host user's UID and GID. Without `--data-root`,
Mainstay continues to use Docker-managed, project-scoped named volumes and the
native account from each service image. Initialization will not change an
existing installation from one root to another; relocating live data requires
an explicit stopped-service migration and corresponding `.env` update.

For bind-mounted installations, Mainstay stores a private recovery copy at
`<instance-root>/.env.recovery`. The instance root itself is not mounted into a
container. The installer creates the copy after configuration is complete and
routine starts refresh it atomically with mode `0600`. Mainstay refuses to
overwrite it when identity-bound secrets differ. This same-disk copy simplifies
reattachment to restored data, but it does not replace an encrypted off-host
backup of `.env` and the instance root.

Recover an existing instance into a fresh deployment directory with:

```bash
./recover-mainstay.sh
```

The recovery wizard requires an existing instance root containing
`.env.recovery` and all five service data directories. It never generates
replacement secrets. The operator may use the existing data-root basename as
the new Compose project name, choose a different Compose name after an explicit
mismatch warning, or abort. Compose and storage names need not match during
recovery; the absolute data sources remain authoritative. To rename a directory
or ZFS dataset, stop the old service set and rename or remount it before running
the recovery wizard. The script itself never renames recovered storage.

An installation created with the wizard marks only its derived instance root;
the parent can safely contain other Mainstay instances. Tear the selected
instance down completely with:

```bash
./teardown-mainstay.sh
```

The teardown command shows exactly what it will remove and requires the literal
confirmation `DELETE`. It runs `docker compose down --volumes`, removes `.env`
and generated installation-identity state, and deletes the derived instance
root, including `.env.recovery`, only when the installer ownership marker is
present. The shared parent and unmarked operator-owned directories are never
recursively deleted. Built images remain available, making the next disposable
installation quicker.

Each installation derives local image tags from `COMPOSE_PROJECT_NAME`, so a
Mainstay build cannot retag an independent service image or another Mainstay
instance's image. Use `./teardown-mainstay.sh --remove-images` to also remove
only this deployment's derived image tags; custom image overrides are retained.

`init-env.sh` copies `.env.example` when `.env` is absent and generates
independent Clear master/operator secrets, a valid Safebox cookie-encryption
key, and a private Safebox onboarding invite code without printing them. It
also fills those entries in an older `.env` when they are missing. The command
is idempotent and restricts `.env` to the current user.
If the configured Clear storage already contains data, it refuses to generate
a missing master secret; recover the original secret instead of assigning a
new identity to an existing mint database. It likewise refuses to generate a
missing cookie key over existing Safebox storage, avoiding accidental
session-key rotation during environment recovery. Preserve `.env` alongside
backups because it records both the identity-bound secrets and storage layout.

Secret initialization does not fund the service Acorn. After its first
successful startup, the operator must provide a mint-fee reserve before relying
on Lightning-address delivery. A healthy worker can create an invoice with no
reserve, then fail after settlement when it attempts to deliver the full amount
as ecash. Mainstay displays this required bootstrap step on the dashboard; it
does not yet measure the remaining reserve automatically.

Fund the default 100-sat reserve while the singleton worker is stopped:

```bash
docker compose stop service-acorn-worker
docker compose run --rm --no-deps service-acorn-worker \
  python -m app.service_acorn_worker fund 100
docker compose up -d service-acorn-worker
```

Pay the displayed invoice and wait for the funding command to confirm the
deposit before restarting the worker. The reserve is operator-owned working
capital, is separate from recipient payments, and must be replenished as mint
fees consume it.

Check the current reserve from the deployed Mainstay directory without
requiring Poetry on the host:

```bash
./reserve-balance.sh
```

The script uses the configured Docker Compose project, briefly stops the
singleton worker, runs its balance command in a one-off container, and restores
the worker only when it was running beforehand. From a development checkout
with Poetry installed, `poetry run mainstay-local reserve balance` remains an
equivalent convenience command.

Mainstay briefly pauses the singleton service Acorn worker while it loads the
persisted wallet, then restores the worker only if it was running beforehand.
The command reports the wallet's current Cash balance without exposing its
recovery key. Lightning-address delivery is paused during this short check.

Mainstay builds `spurline`, `grove`, `clear`, and `safebox-web` directly from
their GitHub `main` branches, so their repositories do not need to be checked
out beside Mainstay. The build-context variables in `.env.example` can instead
select a tag, commit, fork, or local checkout when a deployment needs an exact
version or development source. Remote builds require GitHub access while the
images are being built but add no GitHub dependency to the running containers.
The default deployment starts its own Safebox Web container and cannot replace,
stop, or alter an independently running Safebox Web Compose project.

Spurline is reachable by Mainstay containers as `ws://spurline:8080`, Grove as
`http://grove:8000`, and Clear as `http://clear:3339`. None of those
infrastructure services publishes a host port in the default deployment.
Safebox Web alone publishes host port `8888`. For direct diagnostics from the
Docker host, apply the debug overlay:

```bash
docker compose -f docker-compose.yaml \
  -f docker-compose.debug-ports.yaml up --build --detach
curl http://127.0.0.1:8780/health
curl http://127.0.0.1:8001/health
curl http://127.0.0.1:3340/health
```

The names `spurline`, `grove`, and `clear` are Compose network aliases, not
durable service identities. Containers and volumes use Compose project-scoped
names, allowing these instances to coexist with separately deployed
containers. Debug ports do not change Grove's bundle origin or the canonical
Clear URL encoded into Mint Notes. Safebox Web is registered as an enabled
default service.

## Mainstay Safebox Web

Mainstay starts Safebox Web as one app in the local service graph. It publishes
the Mainstay-owned instance on host port `8888` by default, leaving a
standalone deployment's usual `8000` port untouched:

```bash
./init-env.sh
docker compose up --build --detach
docker compose ps safebox-web
```

The `mainstay-local` Compose project gives this instance its own container and
persistent data source; it does not reuse a standalone Safebox Web project's
state.
Set `MAINSTAY_SAFEBOX_PORT` to another unused host port if `8888` is occupied;
set `MAINSTAY_LOCAL_PORT` similarly when the dashboard port is occupied.

Safebox Web initializes and migrates its SQLite database during application
startup. Mainstay bootstrap owns the secrets that must exist first:
`SAFEBOX_COOKIE_KEY` protects browser sessions and
`SAFEBOX_ONBOARD_INVITE_CODE` controls the initial onboarding route. Preserve
`.env` with the Safebox data volume. The generated invite code can be read by
the operator from `.env`; it is never printed by the helper.

Port `8888` binds to `0.0.0.0`, and Mainstay explicitly enables Safebox's local
HTTP mode. Another trusted machine can therefore open
`http://<host-address>:8888/`. This mode uses non-`Secure` session cookies and
must be limited to a trusted LAN or VPN with a host firewall. Disable
`SAFEBOX_ALLOW_INSECURE_HTTP` and use a TLS-terminating reverse proxy before
exposing Safebox across an untrusted network.

New Acorns use the external Lightning-backed mint at
`https://mint.safebox.dev`. The project-private Clear endpoint remains
separate in `SAFEBOX_CLEAR_MINTS`; it is not used as the Acorn home mint.

Safebox also discovers Clear CMUs from the default external mint at
`https://clear.safebox.dev`. Mainstay supplies both that endpoint and the
managed `http://clear:3339` endpoint through `SAFEBOX_CLEAR_MINTS`. Configure a
different external default with `MAINSTAY_EXTERNAL_CLEAR_MINT_URL`. Registering
the endpoint does not merge its CMUs: balances and trust decisions remain
bound to each complete `cmu-<keyset-id>`.

Mainstay passes only `MAINSTAY_EXTERNAL_CLEAR_MINT_URL` through
`SAFEBOX_CLEAR_EXTERNAL_MINTS` for public NIP-05 advertisement. It never
advertises the Docker-only `http://clear:3339` route. A cross-instance Clear
send may carry tokens from a public HTTPS mint even when the receiver has not
seen that mint before. The managed Mainstay mint remains local-only until an
external route to that same mint is deliberately implemented.

For cross-Mainstay token delivery, configure an externally reachable relay as
the public NIP-05 discovery hint while retaining the private Spurline address as
the wallet home relay:

```env
SAFEBOX_SERVICE_ACORN_HOME_RELAY=ws://spurline:8080
SAFEBOX_NIP05_EXTERNAL_RELAYS=wss://spurline.safebox.dev
```

The external value is forwarded only to Safebox Web. It must not replace the
internal home relay used by wallets and the service Acorn inside Mainstay.

Generated Lightning invoices do not require the local Safebox instance to have
a Lightning address. Conventional Lightning addresses remain optional external
discovery hints because they require DNS and an HTTPS LNURL endpoint. Mainstay
treats the Acorn `npub` as the durable identity and leaves room for Nostr and
FIPS payment discovery without making a domain part of that identity. The open
design questions are recorded under **Payment Identity and Discovery** in the
[address-spaces and FIPS note](docs/ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md#payment-identity-and-discovery).

The singleton service-Acorn worker starts with the default bundle. On its first
successful start it creates a provider Acorn against the internal Spurline
relay and external Lightning mint, then stores its recovery state as
`/app/data/service-acorn.json` in Mainstay's Safebox data source. Routine
restarts recover that same identity. Do not delete or replace the state file
without draining provider obligations and deliberately retiring the worker.

Inspect its startup and retained public identity with:

```bash
docker compose ps service-acorn-worker
docker compose logs service-acorn-worker
```

Mainstay starts Clear in root-bootstrap mode but does not commission it, issue
Mint Notes, or enable treasury activity. The formal Clear commissioning state
machine is not implemented yet. Before issuing anything beyond disposable test
value, choose the canonical `CLEAR_MINT_URL` and optional root authority, then
preserve the database, `CLEAR_MASTER_SECRET`, and root-authority relationship
together. Do not change those values to reconnect an existing database.

The image includes the privileged root CLI, which talks only to Clear's
container loopback interface:

```bash
docker compose exec clear clear-root info
docker compose exec clear clear-root wallet balance
```

For an operator distribution to a Safebox registered in this same Mainstay,
run the context-aware wrapper from the Mainstay checkout on the Docker host:

```bash
poetry run mainstay-local clear send 20 awaycastle559 --memo "hello"
```

The command accepts only a bare local handle. It verifies the handle and Clear
receive capability through the co-resident Safebox directory, selects the
internal Spurline route, and then invokes `clear-root` with its explicit
internal-delivery override. Mainstay does not own or read the root wallet and
does not print the resulting bearer token or proofs. See the
[Clear context wrapper design note](docs/MAINSTAY-CLEAR-CONTEXT-WRAPPER.md) for
the trust boundary and failure behavior.

`init-env.sh` also creates `CLEAR_MINT_SERVICE_NSEC`. Clear derives a stable
mint-service `npub`, records that public identity with its database, and shows
it in `clear-root info` and the Mainstay service report. The identity starts as
`bootstrapped`; it can operate technically but has no recognized operator
attestation until `mainstay-local service commission clear` succeeds. The
service identity is not the currency root and does not itself authorize a
keyset-to-service binding. Preserve `.env` with the Clear data source.

The helper also creates `GROVE_SERVICE_NSEC` and injects it only into Grove.
Grove reports the derived service `npub` on its homepage and records it in its
persistent data as a mismatch sentinel. This bootstrapped identity is
uncommissioned; Mainstay does not yet implement Grove commissioning or signed
endpoint descriptors.

Spurline follows the same model. `init-env.sh` creates
`SPURLINE_SERVICE_NSEC`, injects it only into the relay, and Spurline reports
the derived service `npub` and deterministic FIPS IPv6 address. The identity
is bound to the relay data directory and starts uncommissioned.

Safebox Web has its own application-service identity under the same lifecycle.
`SAFEBOX_WEB_SERVICE_NSEC` is injected only into the web application, which
reports its derived `npub` and FIPS IPv6 address at `/info` and binds that
identity to its persistent data. It is distinct from every user Acorn and from
the provider service Acorn. No signing or commissioning role is implied yet.

Connecting Mainstay to an established external Clear mint is a separate
registry mode and does not reuse this managed-mint volume.

The Docker default publishes port `8788` on `0.0.0.0` so another trusted
machine on the LAN or VPN can reach Mainstay Local:

```text
http://<host-address>:8788/
http://<host-address>:8788/status
```

Use a host firewall or VPN ACL when the host has interfaces that should not
reach the control plane.

On a deployment host, update, rebuild, recreate, and check the managed service
bundle from its dedicated Mainstay deployment directory with:

```bash
./refresh-containers.sh
```

The refresh script refuses tracked working-tree changes, accepts only a
fast-forward source update, and then delegates to the same validated start path
used for routine operation. That path runs `init-env.sh`, so an older
environment gains missing Clear and Safebox secrets and migrates legacy generic
image tags into the deployment's Compose-project namespace before Compose
evaluates the bundle. It waits for both the managed HTTP status check and the
service Acorn's persisted initialization state. Update services owned by this
bundle here rather than by running their standalone repository refresh scripts.

Install and preview the MkDocs site locally:

```bash
poetry install --with docs
poetry run mkdocs serve
```

Then open [http://127.0.0.1:8000/](http://127.0.0.1:8000/).

The published site is [trbouma.github.io/mainstay](https://trbouma.github.io/mainstay/).

## Status

Mainstay is currently a product vision and integration direction. The sibling
components are being developed and proven independently before they are
assembled into the unified application.

## License

MIT
