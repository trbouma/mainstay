# Mainstay

Mainstay is the future unified local-first application for records, identity,
payments, and community resource coordination. It brings the Safebox, Acorn,
Stroma, Grove, Spurline, and Clear product family into one coherent experience across
connected and disrupted conditions.

Mainstay is the application. Lockbox is the appliance. There's no place like
home.

## Documentation

Start with the [first-time start guide](website/getting-started.md) for either
a quick testing deployment or a planned production initialization.

Design notes:

- [Clerk and Treasury Functions](docs/CLERK-AND-TREASURY-FUNCTIONS.md)
- [mainstay-local Hypervisor and FIPS](docs/LOCAL-FIRST-HYPERVISOR-AND-FIPS-DESIGN-NOTE.md)
- [Address Spaces, Endpoint Scopes, and FIPS](docs/ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md)
- [Identity, Resolution, and Event-Native Services](docs/IDENTITY-RESOLUTION-AND-EVENT-NATIVE-SERVICES.md)
- [Service Identity and Operator Attestation](docs/SERVICE-IDENTITY-AND-OPERATOR-ATTESTATION-DESIGN-NOTE.md)
- [Local Clear Transactions](docs/LOCAL-CLEAR-TRANSACTIONS-DESIGN-NOTE.md)
- [Clear Transfer Routing and Reachability](docs/CLEAR-TRANSFER-ROUTING-AND-REACHABILITY.md)
- [Mainstay Clear Context Wrapper](docs/MAINSTAY-CLEAR-CONTEXT-WRAPPER.md)

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

Initialize `.env`, then start the local bundle:

```bash
./init-env.sh
docker compose up --build --detach
docker compose ps
curl http://127.0.0.1:8788/health
```

To choose where persistent service data lives, set the root on the first
initialization:

```bash
./init-env.sh --data-root "$HOME/mainstay-local-data"
docker compose up --build --detach
```

This records the absolute root in `.env` and creates `mainstay-local`,
`safebox-web`, `spurline`, `grove`, and `clear` subdirectories beneath it.
Compose uses those directories as bind mounts and runs the data-writing
processes with the initializing host user's UID and GID. Without `--data-root`,
Mainstay continues to use Docker-managed, project-scoped named volumes and the
native account from each service image. Initialization will not change an
existing installation from one root to another; relocating live data requires
an explicit stopped-service migration and corresponding `.env` update.

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
Set `MAINSTAY_SAFEBOX_PORT` to another unused host port if `8888` is occupied.

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

On a deployment host, pull, rebuild, recreate, and check the managed service
bundle with:

```bash
./refresh-containers.sh
```

The refresh script runs `init-env.sh` after pulling changes, so a new deployment
gets its environment automatically and an older environment gains missing
Clear and Safebox secrets before Compose evaluates the bundle. It waits for
both the managed HTTP status check and the service Acorn's persisted
initialization state.

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
