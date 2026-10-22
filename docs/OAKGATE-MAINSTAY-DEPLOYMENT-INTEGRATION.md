# OakGate and Mainstay Deployment Integration

## Status

This is an architectural review and staged integration direction. It does not
yet change the Mainstay Compose bundle, installer, recovery workflow, or
default web client.

## Decision direction

OakGate can become Mainstay's premier web client because it provides the
managed experience that Mainstay is intended to make ordinary: familiar
sign-in, retained Acorn custody, background receipt handling, records, value,
and a path toward independent operation.

That choice must not erase the distinct Safebox Web model. Safebox Web remains
the non-custodial alternative in which the service does not retain the user's
secret. OakGate becomes the preferred managed client; it does not become the
only valid client or redefine Acorn ownership.

The recommended transition is:

1. add OakGate, Redis, and Keycloak to Mainstay as an integrated deployment
   option;
2. prove local service routing, identity recovery, backup, restore, and live
   sign-in within that bundle;
3. make OakGate the default client after the operational acceptance criteria
   in this note pass; and
4. retain Safebox Web as an optional non-custodial deployment profile rather
   than silently removing it.

## Target service graph

```text
                         public HTTPS
                               |
                       reverse proxy / TLS
                         /             \
                        /               \
                  OakGate             Keycloak
                 premier app        identity service
                    |   \                 |
                    |    \                |
                    |   Redis        durable identity DB
                    |  sessions
                    |
              Acorn operations
                    |
          +---------+---------+
          |         |         |
       Spurline    Grove      Clear
        events     blobs      value
          \         |         /
           \--------+--------/
                    |
              Mainstay Local
        deployment context and status
```

Only OakGate and Keycloak require browser-reachable HTTPS origins. Redis must
remain private to the deployment network. Spurline, Grove, Clear, and the
Mainstay control plane retain their existing scoped exposure rules.

## OakGate's role

OakGate is not a presentation-only replacement for Safebox Web. It currently
owns additional responsibilities:

- the mapping from a Keycloak issuer and subject to one Acorn;
- encrypted custody of Acorn recovery material;
- user preferences and handle reservations;
- durable incoming-payment and record-presentation coordination;
- authenticated value and record workflows; and
- background work that can continue while a browser is closed.

Its SQLite database and `OAKGATE_CUSTODY_KEY` therefore belong to the Mainstay
instance's durable recovery boundary. OakGate's `OAKGATE_SERVICE_NSEC` is a
separate application-service identity and must not be reused as a user Acorn,
installation identity, or Keycloak secret.

OakGate already reports `/health` and `/info`. Mainstay can initially discover
it through the same health and information conventions used for other family
services. Commissioning and operator attestation remain separate future work;
`mainstay-managed` is an ownership label, not proof of commissioning.

## Keycloak in the Mainstay deployment

### Keycloak is durable identity infrastructure

Keycloak is not an incidental login helper. OakGate binds custody to the exact
OIDC issuer and subject. Losing or recreating the realm can assign different
subjects and strand otherwise intact OakGate custody rows. Preserving an email
address or recreating a similarly named user is not sufficient recovery.

For an integrated Mainstay instance, preserve together:

- the Keycloak realm, users, federated-identity links, clients, and credentials;
- the exact public issuer origin;
- OakGate's custody database and custody key;
- the OakGate OIDC client identifier and secret; and
- the proxy, DNS, and TLS configuration that keeps the issuer reachable.

The Mainstay recovery workflow must treat the OakGate and Keycloak snapshots as
one coordinated recovery set. Restoring one from a materially different point
in time can leave authenticated identities without custody rows or custody rows
whose subjects no longer exist.

### Recommended ownership model

The default Lockbox or community installation should operate its own Keycloak
realm as part of the Mainstay instance. A larger operator may run a shared
Keycloak service, but each Mainstay instance still needs an explicit realm,
issuer, backup owner, recovery procedure, and account-deletion boundary.

Sharing a realm across unrelated applications complicates OakGate's future Go
Independent process: OakGate may remove its client access and associations, but
must not delete a shared identity used elsewhere. A dedicated realm gives the
cleanest initial boundary while allowing other identity providers to be linked
to the same Keycloak user.

### Production persistence

OakGate's current Compose file starts Keycloak with `start-dev` and stores its
data in a host directory. That is useful for the present deployment and an
integration spike, but it should not be the final foundation for a premier
Mainstay client.

Before OakGate becomes the default production profile:

- run Keycloak in production mode;
- use a supported durable database, preferably a dedicated PostgreSQL service;
- pin the Keycloak and database image versions;
- keep the database private to the identity network;
- implement a consistent database backup and restore procedure;
- provision the realm and OakGate client reproducibly without committing
  administrator or client secrets; and
- test that a restored realm produces the same issuer and subjects.

PostgreSQL adds another durable service, but it makes the persistence and
backup boundary explicit. Continuing with Keycloak's development store would
make identity the least mature durable dependency in a custody-bearing system.

### Issuer and internal routing

The browser and OakGate must agree on one stable HTTPS issuer, for example
`https://keycloak.example.org/realms/oakgate`. OakGate must validate that exact
issuer even when the two containers share a private network. Replacing it with
`http://keycloak:8080/realms/oakgate` changes the identity namespace and will
not match tokens issued under the public origin.

The deployment therefore needs working internal resolution for the public
issuer or a carefully supported Keycloak back-channel configuration that does
not alter the token issuer. This must be tested from inside the OakGate
container, not only from a browser.

Keycloak's administrator interface and management health port must not be
published as general Mainstay user surfaces. The public realm endpoint and the
operator administration boundary require separate access policy.

## Redis in the Mainstay deployment

Redis has a deliberately narrower role than Keycloak and OakGate SQLite. It
holds login transactions and application sessions; it does not hold Acorn
keys, recovery phrases, Keycloak tokens, or durable payment state.

The integrated deployment should:

- name the service explicitly, such as `oakgate-sessions`;
- expose no host port;
- attach it only to the network used by OakGate;
- keep persistence disabled;
- retain a bounded memory limit and `noeviction`, so capacity failure is
  visible rather than silently removing active sessions;
- preserve the health check and make OakGate depend on Redis readiness; and
- omit Redis from backups and recovery copies.

Restarting Redis should continue to log everyone out without affecting Acorn
custody or payment recovery. A Redis outage must fail session access closed.
This is desirable behavior, not data loss.

The current one-week OakGate session is independent of later Keycloak session
revocation. Before calling OakGate the premier client, either implement
back-channel logout or make this delayed-revocation boundary prominent in the
operator policy and choose an acceptable session lifetime. Mainstay should not
present Keycloak account revocation as immediate OakGate revocation while that
is untrue.

## Mainstay-local integration gaps

### Private service routes

OakGate's current defaults use public HTTPS and WSS endpoints. Its record
storage accepts HTTPS endpoints, relay configuration accepts operator-approved
WSS endpoints, and some metadata paths reject private addresses. Mainstay's
local bundle instead uses scoped private routes such as:

```text
ws://spurline:8080
http://grove:8000
http://clear:3339
```

Do not weaken OakGate's public URL validation globally. Add an explicit
Mainstay deployment context that supplies exact, operator-controlled internal
origins and permits them only on the private Compose network. Public,
user-supplied, and discovered destinations must retain their existing SSRF,
DNS-rebinding, redirect, and secure-transport protections.

This is the principal application change required before OakGate can use the
local Mainstay service graph instead of reaching the same operator's services
through public DNS.

### Contracts currently tied to Safebox Web

Mainstay currently assumes Safebox Web in several places:

- the service registry and dashboard;
- installer questions, port names, image names, and generated environment;
- the `MAINSTAY_SAFEBOX_MANAGEMENT_URL` contract;
- direct read-only access to the Safebox SQLite database;
- the `service-acorn-worker` image, state, reserve, and funding workflow; and
- backup, recovery, teardown, and documentation paths.

OakGate should not imitate those contracts merely to appear interchangeable.
Its users receive directly into their own custodial Acorns, and its durable
jobs live in the OakGate database. The Mainstay control plane needs a
client-neutral capability contract for status and management rather than a
renamed Safebox-specific URL or shared database mount.

Until those dependencies are removed or generalized, Safebox Web and its
service-Acorn worker cannot simply be deleted from the Compose file. The safe
transition is coexistence followed by explicit profile separation.

### Background workers and scale

OakGate currently starts payment, rate, and direct-ecash workers inside the web
application process. The Mainstay profile must initially run one OakGate app
process with one Uvicorn worker. Starting multiple application processes or
replicas also starts multiple background loops. Some durable work uses leases,
but that does not establish that every task is safe or efficient under
replication.

Before scaling OakGate horizontally, separate durable background work into a
dedicated worker command or prove every loop safe under multiple processes.
This is not required for a single Lockbox, but it is an important limit for a
premier hosted deployment.

### Health and readiness

OakGate's `/health` endpoint intentionally reports process liveness without
checking Redis, Keycloak, the custody database, or configured infrastructure.
Mainstay should preserve that meaning and add a distinct readiness contract.

The dashboard should report at least:

- OakGate process liveness;
- Redis session readiness;
- Keycloak realm readiness and public issuer reachability;
- custody database access and service-identity binding;
- local relay, blob, and mint route availability; and
- whether payments or background receipt handling are intentionally disabled.

A failure in Keycloak should not make existing Acorn data disappear. It should
be shown as an authentication outage. A Redis failure should be shown as a
session outage. A relay failure should produce unavailable wallet data rather
than zero balances. These conditions have different recovery actions and must
not collapse into one red or green health indicator.

## Proposed instance storage and secret layout

For a host-backed Mainstay instance:

```text
<instance-root>/
    .env.recovery
    mainstay-local/
    oakgate/
        custody.sqlite3
    keycloak-db/
    spurline/
    grove/
    clear/
```

Redis has no directory. Safebox Web retains its own directory only when its
optional profile is enabled.

The protected recovery environment needs to preserve at least:

- `OAKGATE_CUSTODY_KEY`;
- `OAKGATE_SERVICE_NSEC`;
- `OAKGATE_OIDC_CLIENT_SECRET`;
- the Keycloak bootstrap or operator recovery credentials;
- the Keycloak database credential;
- stable public OakGate and Keycloak origins; and
- image revisions and configuration needed to restore compatible versions.

The custody key and database should also have a separately controlled off-host
backup. A same-disk `.env.recovery` file is operationally convenient but does
not protect against loss of the instance disk.

## Network and exposure model

A useful Compose split is:

| Network | Members | Purpose |
| --- | --- | --- |
| edge | reverse proxy, OakGate, Keycloak | Browser-facing application and OIDC traffic |
| identity | OakGate, Keycloak, Keycloak database | Authentication and identity persistence |
| sessions | OakGate, Redis | Disposable private session state |
| services | OakGate, Mainstay Local, Spurline, Grove, Clear | Scoped local product capabilities |

Compose networks are useful routing boundaries, not complete security
boundaries. Each service must still authenticate sensitive operations, expose
only required ports, run without unnecessary privileges, and validate the
destinations it contacts.

The default integrated bundle should publish only the ports required by the
host reverse proxy and local dashboard policy. Redis, PostgreSQL, internal
Clear surfaces, Grove, and Spurline do not need general host exposure.

## Installer and lifecycle changes

The Mainstay installer will eventually need to:

1. ask for OakGate and Keycloak public origins and host bindings;
2. generate the OakGate custody key, service key, OIDC client secret input,
   Keycloak administrator recovery secret, and database credential without
   printing them unnecessarily;
3. create correctly owned OakGate and identity-database directories;
4. provision or verify the Keycloak realm and confidential OakGate client;
5. record OakGate and Keycloak state in `.env.recovery`;
6. validate that both public origins use HTTPS outside loopback;
7. test the issuer from both the browser-facing route and OakGate container;
8. include OakGate, Keycloak, and the identity database in start, refresh,
   backup, restore, and teardown procedures; and
9. offer Safebox Web as an explicit non-custodial profile rather than starting
   both clients without an operator decision.

Do not automate destructive realm replacement. If Keycloak data already
exists, initialization must refuse to generate a new identity store over it in
the same way Mainstay currently refuses to generate replacement secrets over
existing service data.

## Staged implementation

### Phase 1: integration profile

- Add OakGate, private Redis, and the current Keycloak deployment behind an
  explicit Compose profile or override.
- Add OakGate to Mainstay's service registry and dashboard.
- Preserve Safebox Web and the service-Acorn worker unchanged.
- Add exact internal-route support to OakGate without weakening public URL
  validation.
- Exercise live sign-in, Acorn creation/reconnection, balances, records,
  direct value transfer, and failure behavior.

This phase proves wiring; it does not make the current Keycloak development
store production-ready.

### Phase 2: durable identity and lifecycle

- Move Keycloak to production mode with PostgreSQL.
- Add coordinated backup and isolated restore procedures.
- Integrate all identity and custody secrets into Mainstay initialization and
  recovery safeguards.
- Add readiness reporting and exercise Redis loss, Keycloak loss, and public
  issuer unavailability separately.
- Test an alternative identity provider linked to the same Keycloak user.

### Phase 3: default-client transition

- Generalize or retire Safebox-specific Mainstay management contracts.
- Make OakGate the default managed-client profile.
- Move Safebox Web to an explicit non-custodial profile.
- Update first-start, recovery, dashboard, and product documentation.
- Keep migrations reversible at the deployment level; choosing OakGate must
  not rewrite an existing Safebox Web user's custody model.

### Phase 4: departure and scale

- Complete and test Go Independent, including in-flight work and restore
  safeguards against resurrecting departed custody.
- Separate background workers before multi-process or multi-replica hosting.
- Add commissioning and operator-attestation evidence for OakGate if the
  family service contract requires it.

## Acceptance criteria before OakGate becomes the default

1. A new Mainstay instance can install OakGate, Redis, Keycloak, and durable
   identity storage without manual edits to Compose.
2. The same public issuer works from browsers and from inside OakGate.
3. OakGate uses Mainstay's local Spurline, Grove, and Clear services through
   explicitly trusted internal routes.
4. Redis restart logs users out without losing custody, records, balances, or
   recoverable payment work.
5. A coordinated OakGate and Keycloak backup restores the same test user to the
   same Acorn identity in an isolated environment.
6. Losing Keycloak, Redis, a relay, or a mint produces a distinct and honest
   status rather than a zero balance or generic healthy state.
7. Keycloak runs in production mode on supported durable persistence.
8. Mainstay never logs or displays the custody key, OIDC client secret, user
   recovery phrase, or Keycloak administrator credentials.
9. Safebox Web remains installable as a documented non-custodial alternative.
10. The operator and user documentation states that OakGate is custodial and
    distinguishes implemented recovery disclosure from tested independent
    recovery and the still-incomplete Go Independent workflow.

## Immediate next work

The first code change should be a non-default Compose integration profile and
client-neutral registry entry, accompanied by tests. Before wiring local
services into that profile, OakGate needs a narrowly scoped trusted-local-route
configuration for the exact Mainstay service origins. Keycloak production
persistence can follow in the durable-identity phase, but OakGate should not
become the default client until that work and an isolated restore test are
complete.
