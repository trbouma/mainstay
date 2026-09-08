# First-Time Start

Mainstay can be running quickly for local testing. A production installation
needs a more deliberate first start because its storage layout, service keys,
mint identity, public routes, and recovery material become part of the durable
operating context.

!!! warning "Use one deployment directory for each Mainstay instance"

    A Mainstay deployment directory owns one instance's `.env`, Compose
    lifecycle, generated installation identity, and teardown authority. Create
    a separate checkout or deployment directory for every instance. Do not run
    multiple instances from one directory and do not share `.env` files between
    deployment directories. Assign every directory a unique
    `COMPOSE_PROJECT_NAME` so its containers, network, and named volumes cannot
    collide with another instance on the same host.

## Quick Testing Start

Use this path for disposable testing on a trusted machine. It accepts the
development defaults: Docker-managed volumes, HTTP on the local network,
GitHub `main` build contexts, an internal-only Clear mint, and generated local
secrets.

Prerequisites are Git, Docker with Compose, and enough disk space to build and
run the service images.

```bash
git clone https://github.com/trbouma/mainstay.git
cd mainstay
./install-mainstay.sh
docker compose ps
```

The wizard asks for a unique Compose project name, the dashboard and Safebox
Web host ports, their bind addresses, and one data root for all service data.
Press Enter to accept a displayed default. Enter `abort`, `quit`, or `q` at any
prompt to leave without writing configuration. The final confirmation defaults
to no. Before that confirmation, a read-only preflight checks Docker, Compose,
OpenSSL, the Compose namespace, data-root writability, and selected host-port
availability.

Open the Mainstay dashboard at `http://127.0.0.1:8788/` and Safebox Web at
`http://127.0.0.1:8888/`. To retrieve the generated onboarding path without
printing the other secrets:

```bash
awk -F= '$1 == "SAFEBOX_ONBOARD_INVITE_CODE" { print $2 }' .env
```

Open `http://127.0.0.1:8888/onboard/<invite-code>` to create the first Acorn.
For access from another trusted LAN or VPN machine, replace `127.0.0.1` with
the Mainstay host address. Browser camera access generally requires HTTPS when
the page is not on loopback.

Check the bundle and inspect a service that is not healthy:

```bash
curl http://127.0.0.1:8788/health
curl http://127.0.0.1:8788/status
docker compose ps
docker compose logs --tail 100 <service-name>
```

At this point Safebox, the internal relay, Grove, Clear, and the service-Acorn
worker are running. Clear is bootstrapped but its service identity is not yet
commissioned, its treasury gate is closed, and the service Acorn has no
operator-funded mint-fee reserve.

For a completely disposable test installation, run:

```bash
./teardown-mainstay.sh
```

After the explicit `DELETE` confirmation, it removes the Compose containers,
network, named volumes, generated `.env`, and installation identity state. A
bind-mounted root is deleted only when it carries the installer's ownership
marker; unmarked operator-owned directories are preserved. Component images
remain cached for a quicker reinstall.

## Optional Testing Milestones

Install the Mainstay host CLI and commission Clear under the generated
Mainstay installation authority:

```bash
poetry install --with dev,docs
poetry run mainstay-local service commission clear
poetry run mainstay-local service verify clear
```

Verify Clear's accounting path and explicitly open its treasury gate before
issuing test Clear value:

```bash
docker compose exec clear clear-root treasury status
docker compose exec clear clear-root verify
docker compose exec clear clear-root treasury enable
docker compose exec clear clear-root treasury status
```

Fund the service Acorn before testing Lightning-address delivery. Keep its
singleton worker stopped while the funding command owns the wallet:

```bash
docker compose stop service-acorn-worker
docker compose run --rm --no-deps service-acorn-worker \
  python -m app.service_acorn_worker fund 100
docker compose up -d service-acorn-worker
```

Pay the invoice displayed by the funding command and wait for confirmation
before restarting the worker.

## Production Decisions

Make these decisions before the first stateful `docker compose up`. Several of
them can be migrated later, but none should change merely to repair a routing
or configuration problem.

### Operating context

Define who operates the Mainstay instance, who may commission it, who can
recover it, and whether it is autonomous or subordinate to a higher authority.
Choose how operator attestations and recovery evidence will be retained.

### Persistent storage

Choose a durable filesystem with adequate capacity, monitoring, encryption,
and backup support. Select its root during first initialization:

```bash
./init-env.sh --data-root /absolute/path/to/mainstay-data
```

Mainstay creates separate `mainstay-local`, `safebox-web`, `spurline`, `grove`,
and `clear` directories beneath that root. Omitting the option uses
Docker-managed named volumes. The initialization helper will not silently move
an existing installation to another root.

### Key and secret custody

The generated `.env` contains identity-bound and encryption material. In
particular, preserve the Mainstay installation key, Clear master secret, Clear
service key, Safebox cookie key, operator token, and onboarding controls.
Store an encrypted backup separately from the live data backup and document
who can restore it. Losing `.env` while retaining the databases may make the
installation unrecoverable; replacing its values may create different
identities rather than recover the old ones.

### Clear mint role

Decide whether the managed Clear mint is internal-only or redeemable by other
Mainstay and independent Safebox installations. `CLEAR_MINT_URL` is encoded in
Mint Notes as a route hint and must be chosen before issuing value:

- `http://clear:3339` is reachable only inside this Compose network.
- A public mint needs a stable externally reachable HTTPS URL and reverse
  proxy before external recipients can redeem its tokens.

Also decide the root-authority npub, currency name and aliases, maximum order,
issuance governance, and who may enable or disable treasury operations. The
Clear master secret and database must always be preserved together.

### Relay and federation policy

Internal transfers use `ws://spurline:8080`. Decide whether users must also
communicate with other Mainstay or independent Safebox instances. When they
must, configure `SAFEBOX_NIP05_EXTERNAL_RELAYS` with one or more reachable
`wss://` relays. Do not advertise the Docker-only relay to external recipients.

Record which routes are internal, locally reachable, externally reachable, or
eventually FIPS-resolved. Service npubs and Clear keyset IDs remain the stable
identifiers; URLs and relay routes are replaceable reachability information.

### Network exposure and TLS

Decide which clients may reach ports `8788` and `8888`. A production reverse
proxy should terminate TLS, forward to the Mainstay host over a trusted path,
and set `X-Forwarded-Proto`, `X-Forwarded-For`, and `Host`. Configure
`FORWARDED_ALLOW_IPS` to the proxy's actual source address and set
`SAFEBOX_ALLOW_INSECURE_HTTP=false` once HTTPS is authoritative.

Bind services to loopback when only a same-host proxy should reach them. If
they bind to `0.0.0.0`, enforce the intended LAN or VPN boundary with firewall
and VPN policy. Spurline, Grove, and Clear remain unexposed by the default
Compose file.

### Software versions

The testing defaults build service images from each repository's GitHub
`main` branch. Production should pin every `MAINSTAY_*_BUILD_CONTEXT` to a
reviewed tag or commit, record the deployed versions, and test upgrades against
a restored copy of production data.

### Backup and recovery

Define a stopped-service backup procedure for the selected data root or named
volumes plus `.env`. Include restoration tests, retention, off-host copies,
available disk-space monitoring, and the acceptable loss window. A backup is
not complete until the operator has demonstrated that it can restore the same
service npubs, Clear keysets, wallet state, records, and relay history.

## Production First Start

Use this order once the decisions above are recorded:

1. Pin the Mainstay and component source revisions.
2. Select and prepare the persistent data root.
3. Run `./install-mainstay.sh`, answer `no` when asked to start, and use the
   review screen to prepare `.env` without starting stateful services.
4. Edit `.env` with the chosen Clear URL and policy, public relay routes,
   ports, bind addresses, reverse-proxy trust, TLS policy, and pinned contexts.
5. Back up the completed `.env` through the approved secret-custody process.
6. Run `./start-mainstay.sh`; it validates interpolation, builds the images,
   starts the bundle and waits for healthy status.
7. Verify the dashboard and each internal service report.
8. Commission the Clear service identity under the Mainstay installation.
9. Run `clear-root verify`, review its result, and explicitly enable treasury
    operations only if local policy permits issuance.
10. Fund and verify the service-Acorn fee reserve before accepting
    Lightning-address payments.
11. Test local Safebox transfer, external relay delivery where enabled, Clear
    redemption from every intended context, and reverse-proxied HTTPS access.
12. Take and restore the first complete backup before onboarding production
    users or issuing non-disposable value.

## Values That Must Move Together

Treat these as recovery units:

| Durable state | Required companion material |
| --- | --- |
| Mainstay installation identity | `MAINSTAY_INSTALLATION_NSEC` and its public sentinel |
| Clear mint database and root wallet | `CLEAR_MASTER_SECRET`, service nsec, operator policy, and canonical mint URL |
| Safebox database and service-Acorn state | Safebox cookie key, configured relays and mints, and payment reserve records |
| Grove data | `GROVE_SERVICE_NSEC`, Grove endpoint, and authorization policy |
| Spurline database | Relay identity, access policy, and advertised routes |

Stopping a container, rebuilding an image, or changing a route should not
change these identities. Changing identity-bound secrets or attaching an old
database to a new identity is a recovery or migration operation, not ordinary
configuration.
