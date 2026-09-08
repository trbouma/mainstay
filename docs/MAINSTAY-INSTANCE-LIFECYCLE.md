# Mainstay Instance Lifecycle and Recovery

Status: implemented operating model  
Date: 2026-09-08

## Purpose

This note defines how a Mainstay instance is installed, started, refreshed,
backed up, recovered and destroyed. The model is designed for three immediate
needs:

1. create a test instance quickly without colliding with another deployment;
2. make persistent state visible and recoverable outside Docker; and
3. preserve the same instance and service identities when containers, hosts or
   storage paths change.

It also establishes a directory layout that can later map onto ZFS datasets and
FreeBSD jails without changing the logical ownership of the data.

## Terms

| Term | Meaning |
| --- | --- |
| Mainstay instance | The complete operational unit: control plane, Safebox Web, Spurline, Grove, Clear, service Acorn, configuration and identities |
| Deployment directory | One checkout or release directory containing Compose files, scripts and the active `.env` for exactly one instance |
| Compose project name | Replaceable Docker namespace for an instance's containers, network and named volumes |
| Data parent | Host directory under which one or more instance roots may live |
| Instance data root | Complete persistent filesystem boundary for one Mainstay instance |
| Data-directory name | Basename of the instance data root; normally equal to the Compose project name on first installation |
| `mainstay-control` | Persistent data for the Mainstay dashboard and coordination process, not the complete instance |
| `.env` | Active deployment configuration and secret material in the deployment directory |
| `.env.recovery` | Mode-`0600` recovery copy stored at the instance root outside all service mounts |

The current CLI and Compose service remain named `mainstay-local` for
compatibility. A future `mainstayctl` command may become a clearer operator
interface, but that rename is not part of the storage model.

## Instance Boundary

Every Mainstay instance runs from its own deployment directory and uses a
unique Compose project name on a shared Docker host. A deployment directory
owns its own:

- `.env`;
- Compose lifecycle;
- generated installation-identity state;
- selected host ports; and
- teardown authority.

Do not run multiple instances from one deployment directory. Do not share one
active `.env` between deployment directories.

For a new instance named `mainstay-testlab` with data parent
`/mnt/bitcoin/mainstay`, the layout is:

```text
/testlab/mainstay/                              deployment directory
└── .env                                       active configuration

/mnt/bitcoin/mainstay/                         shared data parent
└── mainstay-testlab/                          instance data root
    ├── .mainstay-local-managed-data-root      teardown ownership marker
    ├── .env.recovery                          host-only recovery configuration
    ├── mainstay-control/                      control-plane data
    ├── safebox-web/                           app database and Acorn state
    ├── spurline/                              relay database
    ├── grove/                                 blob data and identity sentinel
    └── clear/                                 mint database and root wallet
```

Only the service-specific child directories are mounted into containers. The
instance root, its ownership marker and `.env.recovery` are not mounted into a
service.

## Naming

A fresh installation normally records:

```dotenv
COMPOSE_PROJECT_NAME=mainstay-testlab
MAINSTAY_DATA_PARENT=/mnt/bitcoin/mainstay
MAINSTAY_DATA_DIRECTORY_NAME=mainstay-testlab
MAINSTAY_DATA_ROOT=/mnt/bitcoin/mainstay/mainstay-testlab
```

The installer derives `MAINSTAY_DATA_ROOT` from the parent and data-directory
name, then records absolute service data sources beneath it.

The Compose name and data-directory name are operational labels, not stable
service identities. During recovery they may differ:

```dotenv
COMPOSE_PROJECT_NAME=private-venue-v2
MAINSTAY_DATA_DIRECTORY_NAME=mainstay-testlab
MAINSTAY_DATA_ROOT=/mnt/bitcoin/mainstay/mainstay-testlab
```

This does not change Mainstay's installation `npub`, the service `npub`s,
Clear's keysets or any wallet identity. The absolute data sources remain
authoritative.

## Lifecycle Commands

| Operation | Command | Contract |
| --- | --- | --- |
| First installation | `./install-mainstay.sh` | Gather choices, run read-only preflight, generate initial secrets after confirmation, optionally start |
| Routine start | `./start-mainstay.sh` | Complete safe initialization, refresh recovery copy, validate Compose, start and wait for readiness |
| Code and image refresh | `./refresh-containers.sh` | Pull source and delegate recreation to the canonical start path |
| Save recovery configuration | `./save-recovery-env.sh` | Atomically refresh `.env.recovery` without accepting identity mismatch |
| Recovery | `./recover-mainstay.sh` | Attach a fresh deployment directory to existing state without generating secrets |
| Destructive teardown | `./teardown-mainstay.sh` | Remove one Compose project and only installer-marked bind data after explicit confirmation |

## First Installation

Run from the instance's dedicated deployment directory:

```bash
./install-mainstay.sh
```

The wizard gathers:

- a unique Compose project name;
- a data parent, or an explicit choice to use Docker-managed volumes;
- dashboard bind address and host port;
- Safebox Web bind address and host port; and
- whether to start after configuration.

When `.env` exists, its values are displayed as defaults. When an entry is
absent, the code default is displayed. Entering `abort`, `quit` or `q` stops the
wizard. The final write confirmation defaults to no.

Before that confirmation, the installer checks:

- Docker, Compose, the Docker daemon and OpenSSL;
- project-name syntax and an existing Compose namespace;
- data-root path safety and writability;
- whether a new root is empty or already carries the Mainstay marker;
- host-port syntax, duplication and occupancy; and
- whether an existing deployment is attempting an implicit data-root change.

After confirmation, `init-env.sh` creates the service directories and
cryptographic material, the installer writes the selected values, and
`save-recovery-env.sh` creates `.env.recovery`. Starting services is separate
from commissioning, Clear treasury enablement and service-Acorn reserve
funding.

## Routine Start and Refresh

Use:

```bash
./start-mainstay.sh
```

The start path:

1. verifies Docker and Compose;
2. completes only safe missing initialization;
3. refreshes `.env.recovery`;
4. validates Compose interpolation;
5. builds and starts the service bundle;
6. waits for the Mainstay status surface; and
7. waits for the service-Acorn worker health check.

`refresh-containers.sh` first pulls the deployment repository, then uses the
same start path with forced container recreation. It does not maintain a
separate readiness implementation.

## Recovery Configuration

For bind-mounted installations, the active `.env` is copied atomically to:

```text
<instance-data-root>/.env.recovery
```

The file is mode `0600`. Before replacing an existing recovery copy,
`save-recovery-env.sh` compares identity-bound values including:

- `MAINSTAY_INSTALLATION_NSEC`;
- `CLEAR_MASTER_SECRET`;
- Clear, Spurline and Grove service keys; and
- `SAFEBOX_COOKIE_KEY`.

A mismatch stops the update and preserves the previous recovery copy. This is
intended to catch accidental identity replacement, not to prohibit a planned
rotation procedure.

`.env.recovery` contains secrets. It must never be served, logged, committed or
mounted into a container. Because it resides on the same storage system as the
data, it is a convenient recovery companion but not an independent backup.
Maintain an encrypted off-host copy as well.

## Recovery

Recovery attaches a new deployment directory and Docker runtime to an existing
instance data root. It is not bootstrap and must never generate replacement
secrets.

Prerequisites:

- the old service set is stopped and cannot write to the data;
- the complete instance root is present;
- `.env.recovery` is present at that root;
- the new deployment directory has no `.env`; and
- the selected host ports are available.

Run:

```bash
./recover-mainstay.sh
```

The script verifies the recovery material, accepts both `mainstay-control` and
the legacy `mainstay-local` control-data directory, checks every service data
directory, verifies Docker namespaces and ports, and validates Compose before
writing deployment configuration.

### Name choice

Recovery presents three deliberate paths:

1. use the existing data-root basename as the new Compose project name;
2. supply a different Compose project name after acknowledging the mismatch;
3. abort to rename or remount the storage first.

The script never renames a directory, filesystem, mount point or ZFS dataset.
If the operator wants a new data-root name, all services must remain stopped
while that change is completed before recovery. When names remain different,
the recovery environment records both explicitly and binds Compose to the
existing absolute paths.

After final confirmation, the script writes a mode-`0600` `.env` into the new
deployment directory, rewrites only host-dependent paths, ownership, ports,
bind addresses and Compose namespace, and then refreshes `.env.recovery`.

The old and new Compose projects must never run concurrently against the same
SQLite databases, wallet state or relay database.

## Destructive Teardown

Run from the deployment directory that owns the instance:

```bash
./teardown-mainstay.sh
```

The script displays the exact data root and requires the literal confirmation
`DELETE`. It then runs Compose down with volume and orphan removal, deletes the
deployment `.env` and generated installation-identity state, and removes a
bind-mounted instance root only when the exact installer marker is present.

An unmarked directory is preserved even after explicit confirmation. The data
parent is never removed merely because an instance beneath it was deleted.
Built images remain cached to make recreation faster.

Teardown is destruction, not a backup or migration operation. Copy required
data and recovery material before invoking it.

## Backup Unit

The minimum recoverable unit is:

```text
instance data root + matching .env or .env.recovery
```

The data root contains application state but cannot reconstruct every secret.
The environment contains keys and policy but cannot reconstruct wallet, mint,
relay or blob state. Preserve them together at the same recovery point.

For a consistent filesystem backup, stop the instance first:

```bash
docker compose stop
```

After the backup completes:

```bash
docker compose start
```

An operational backup process should also record image or source revisions,
test restore procedures and retain encrypted off-host copies.

## ZFS Direction

The filesystem layout maps naturally to a parent dataset and child datasets:

```text
tank/mainstay/mainstay-testlab
tank/mainstay/mainstay-testlab/mainstay-control
tank/mainstay/mainstay-testlab/safebox-web
tank/mainstay/mainstay-testlab/spurline
tank/mainstay/mainstay-testlab/grove
tank/mainstay/mainstay-testlab/clear
```

This can support instance-level snapshots and replication while allowing
service-specific compression, quotas or snapshot frequency. Snapshotting child
datasets independently does not automatically create an application-consistent
recovery point; databases and wallet state still need coordinated quiescence or
an explicitly tested snapshot protocol.

ZFS dataset renames, receives and mount-point changes occur outside Mainstay
while services are stopped. The recovery script then records the resulting
absolute paths and attaches the selected Compose namespace.

## Compatibility

- Existing installations with a `mainstay-local` control-data directory remain
  valid and are not silently moved to `mainstay-control`.
- Existing explicit `MAINSTAY_LOCAL_DATA_SOURCE` values remain authoritative.
- Existing deployments without `COMPOSE_PROJECT_NAME` continue to use
  `mainstay-local`.
- Docker-managed volumes remain supported when no data parent is selected, but
  do not receive an in-root `.env.recovery` because no host instance root
  exists.
- A changed host port affects reachability, not service identity. The dashboard
  reads the configured Safebox host port rather than assuming `8888`.

## Safety Invariants

1. One deployment directory owns one Mainstay instance.
2. Compose project names are unique among instances on one Docker host.
3. No two running service sets attach to the same instance data root.
4. Recovery never generates identity-bound secrets.
5. Routine startup never silently changes an existing data root.
6. Recovery never renames storage.
7. Teardown recursively removes only an installer-marked instance root.
8. The shared data parent is not an instance and is not a teardown target.
9. `.env.recovery` stays outside all container mounts and is never public.
10. Same-disk recovery material does not replace an encrypted off-host backup.
