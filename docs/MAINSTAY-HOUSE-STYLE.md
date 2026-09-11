# Mainstay House Style and Family Audit

Status: working standard  
Audit date: 2026-09-11

## Purpose

The Mainstay house style is the shared way the product family presents itself,
defines boundaries, reports operational state, and enters service. It is not a
single color palette or a requirement that every repository become a service.

The standard has four goals:

1. A person should recognize that the products belong together.
2. An operator should encounter the same lifecycle and status vocabulary.
3. An integrator should be able to discover identity and health without
   learning implementation-specific secrets.
4. A fresh Mainstay installation should start predictably once its durable
   configuration and secrets have been selected.

The family principle is **good boundaries, not barriers**. Shared conventions
make components easier to combine while preserving their independent roles.
The companion
[ecosystem responsibility note](ECOSYSTEM-RESPONSIBILITY-BOUNDARIES-AND-ITERATION.md)
defines how those roles are assigned during cross-repository development.

## Applicability

The family contains four different kinds of component:

| Kind | Components | Applicable service requirements |
| --- | --- | --- |
| User and control-plane applications | Mainstay Local, Safebox Web | Human interface, operational health, clear authority boundaries |
| Independently addressable services | Clear, Grove, Spurline | Service identity, health and information surfaces, persistent identity binding |
| Embedded protocol components | Acorn, Stroma | Package, documentation, security and boundary conventions; no network service identity merely for being imported |
| Adjacent protocol applications | OpenETR | Shared evidence, recognition, presentation and deployment conventions without implying that OpenETR is part of the local runtime bundle |

Acorn identities identify Acorns that control keys and resources. They are not
identities for the Acorn Python package. Stroma is a protocol library and does
not acquire a service identity unless a separately addressable Stroma-based
service is created.

Safebox Web is an application around user Acorns and a provider service Acorn.
Those identities must not be silently reused as a Safebox Web application
identity. A dedicated application identity remains a future decision.

## Product Presentation

### Shared anatomy

Family documentation sites use a common sequence:

- the product name as the primary heading;
- the product logo as an immediate visual signal;
- one direct tagline and a short introductory statement;
- a small set of primary actions;
- three or four responsibility-focused capability blocks;
- an explicit boundary statement describing what the product does not own;
- its relationship to the Mainstay family; and
- an honest project-status or experimental-software statement.

Runtime service pages use a quieter operational form:

- compact product header and live status;
- the advertised endpoint with a copy action when useful;
- protocol and capacity information;
- service identity, FIPS address, management mode and commissioning state;
- operator identity when commissioned; and
- links to health, protocol documentation and product documentation.

### Visual family resemblance

The family shares restrained geometry, clear information hierarchy, visible
focus states, responsive grids, readable code values and strong contrast. Text
must wrap safely around long `npub`, keyset, digest, IPv6 and URL values.

Each product retains a distinct palette:

| Product | Visual character |
| --- | --- |
| Mainstay | blue, navy, amber, green and coral; dependable coordination |
| Safebox Web | deep teal, copper and gold; a calm human workspace |
| Acorn | green and warm earth; portable custody and growth |
| Grove | forest and wood; durable storage |
| Spurline | navy, signal blue and amber; local network movement |
| Clear | water teal and coral; bounded issuance and redemption |
| Stroma | violet and stone; layered protocol structure |
| OpenETR | blue, gold and neutral document tones; independently verifiable evidence |

Shared style does not mean recoloring every product Mainstay blue. Logos,
palettes and metaphors remain specific to each responsibility. Operational
interfaces should favor clarity over marketing composition, keep cards to
individual repeated items or bounded tools, and avoid placing critical state
inside decorative layers.

### White-label inheritance

White-labelled deployments use the same semantic presentation system without
requiring Mainstay or Safebox Web to remain the public-facing name. Branding is
resolved in layers:

```text
native product defaults
    -> Mainstay-managed base profile
    -> instance-managed override
    -> one validated effective profile
```

Mainstay owns profile validation, resolution, activation and rollback. Each
instance selects one base profile and may override only the presentation fields
allowed by that profile. Safebox Web and the Mainstay dashboard consume the
same resolved snapshot; they do not merge profile layers independently.

White labelling changes presentation, not authority. It must not alter service
identities, member keys, mint units, keysets, signed evidence, commissioning
relationships, endpoint scope or security and recovery language. Operator
surfaces continue to identify Mainstay and the actual component names even when
routine member surfaces use only the experience owner's brand.

The detailed package, inheritance and lifecycle contract is defined in
[White-Label Branding and Experience Profiles](WHITE-LABEL-BRANDING-DESIGN-NOTE.md).

### Localization ownership

Each application owns its interface strings, translation catalogs, supported
language list and contextual review. Mainstay may carry an instance default and
coordinate a member's preferred BCP 47 language tag, but it does not translate
another component's messages or claim support on that component's behalf.

Safebox Web's server-side localization model is the family reference for
member-facing applications. Supporting services should localize their compact
browser home pages as time permits, while keeping APIs, protocol identifiers,
service identities, endpoint values and machine-readable error codes stable.
Missing translations fall back honestly to the application's own default
language.

White-label profiles own translations of brand-specific copy such as taglines,
descriptions and approved local terminology. They must not override protected
security, recovery, custody or transaction language. A member's supported
language preference takes precedence over the instance default.

The shared behavioral contract, implementation profiles, locale precedence,
review expectations and release checklist are defined in the
[Product-Family Localization Design Note](LOCALIZATION-DESIGN-NOTE.md).

### Language

Use plain role and state language:

- **local-first**, not isolated or local-only;
- **Cash Balance** for the sat-denominated Cashu view;
- **Clear Balances** for distinct issuer-defined CMUs;
- **Mint Note** for a Clear bearer note;
- **service identity** for the stable key of an addressable service;
- **installation identity** for the Mainstay control plane and local authority;
- **operator** for an authority that runs or commissions a service;
- **endpoint** or **route** for replaceable network-path information; and
- **reported**, **pending**, **confirmed** and **verified** only when the
  implementation can support the corresponding claim.

Do not call a URL an identity. Do not call possession of an `nsec` legal
ownership. Do not imply that a friendly currency label makes different
keysets or issuers interchangeable.

### Availability and reachability

Use **availability** for the security and operating outcome: authorized people
can obtain and use the required service, information or value when it is
needed. This is the availability element of the familiar confidentiality,
integrity and availability (CIA) triad.

Use **reachability** only for the narrower network fact that an eligible path
to an endpoint exists from the caller's current scope. Reachability can
contribute to availability, but it does not establish it. A reachable process
may be unhealthy, uncommissioned or unable to complete the requested work. A
service may remain available through another route after one endpoint becomes
unreachable.

User-facing and governance-facing copy should normally say **available**,
**unavailable** or **usable**. Routing, endpoint-scope, FIPS and diagnostic
documents may use **reachable** and **reachability** when the network path is
the actual subject. Do not infer identity, authority, recognition, acceptance
or trust from either condition.

For Clear balances, use three derived availability states and plain-language
wallet labels:

- **Instance**, shown as **Within this instance**, means usable by members
  served by one Mainstay instance. Add its configured display name when useful;
- **Local**, shown as **On the local network**, means usable between
  participating instances over shared local infrastructure without requiring
  internet access; and
- **Across networks** means eligible routes cross the local network boundary.

All Clear bearer transfers remain cryptographically private. Privacy describes
the confidentiality mechanism, not an availability boundary, and must not be
used as an availability label. These states do not imply acceptance,
recognition, treasury authority, or universal access, and they are not
permanent token properties.

Where a security posture is summarized, use the full triad:

- **confidentiality** protects appropriate limits on access and disclosure;
- **integrity** protects the accuracy, authenticity and traceability of
  information and actions; and
- **availability** keeps authorized access and practical use dependable when
  needed.

### Voice and message

The family speaks in a calm, practical and cooperative voice. Lead with what
people can do in ordinary operations, then explain continuity during changing
conditions as an additional benefit.

- Describe **cooperative independence**: local capability that continues to
  work with regional institutions, hosted providers and open networks.
- Describe **local stewardship and shared governance**: communities and
  organizations can operate documented rules for access, issuance,
  recognition and reconciliation together.
- Prefer concrete operating conditions such as intermittent connectivity,
  provider changes, site moves and service interruptions over catastrophe or
  collapse language.
- Present boundaries as a way to make responsibilities understandable and
  cooperation dependable, not as a struggle against institutions or
  infrastructure.
- State limits plainly without letting warnings dominate the product promise.
- Use **when conditions change** as the broad continuity frame. Use
  **emergency preparedness** only where emergency operation is the actual
  subject.

The family does not frame local operation as rebellion, technological
self-sufficiency or withdrawal. It gives people and institutions a dependable
local home from which they can cooperate on clearer terms.

Mainstay may use **Our House. Our Rules. Our Business.** as a governance
statement when the surrounding copy makes its meaning explicit:

- **our house** means a locally operated domain with clear stewardship;
- **our rules** means documented, legitimate and accountable procedures within
  that community or organization's authority; and
- **our business** means ordinary local work and the reasonable expectation
  that confidential affairs are not exposed by default.

The line does not imply disregard for law, outside obligations, voluntary
participants or interoperable relationships. Keep **There's no place like
home.** as the welcoming general tagline; use the governance statement where
local policy, privacy and autonomy are already being explained.

## Identity and Commissioning

### Stable identifiers

- A service `npub` identifies an independently addressable logical service.
- A complete Cashu keyset ID identifies a mint keyset and remains the stable
  anchor for its proofs.
- A Grove blob digest identifies exact bytes.
- URLs, Docker names, DNS names, local addresses and future FIPS routes are
  transport or resolution data, not durable identity.

The deterministic FIPS IPv6 address derived from a service `npub` is reported
with the identity. It is a resolution address derived by FIPS, not a substitute
for the `npub`.

### Lifecycle vocabulary

| State | Meaning |
| --- | --- |
| `unconfigured` | No service key has been supplied. |
| `bootstrapped` or `uncommissioned` | The service controls and persists its key and may operate technically, but no recognized operator attestation is active. New services should report `uncommissioned`; `bootstrapped` may remain in older detailed workflows where possession must be distinguished explicitly. |
| `commissioned` | The service has verified and retained the required commissioning evidence. |
| `active` | The component is operational. This may supplement, but must not erase, commissioning state. Mainstay uses it for its self-managed installation identity. |
| `revoked` or `retired` | Prior authority has been explicitly withdrawn or the service has been deliberately removed from service. |

Bootstrap creates enough technical state to run. Commissioning establishes a
recognized operating relationship. Operational readiness is a separate check:
a commissioned service may still be unhealthy, unfunded or policy-disabled.

### Public identity envelope

Addressable services report this non-secret shape from their information
surface:

```json
{
  "service_identity": {
    "npub": "npub1...",
    "fips_ipv6_address": "fd..:....",
    "type": "clear-mint",
    "management": "independent",
    "state": "uncommissioned",
    "descriptor_event_id": null,
    "operator": null
  }
}
```

When commissioned, `operator` contains only public evidence:

```json
{
  "npub": "npub1...",
  "attestation_event_id": "...",
  "status": "verified"
}
```

No information response, dashboard, log or error may expose an `nsec`, seed
phrase, Clear master secret, cookie key, bearer proof, token, operator token or
private commissioning input.

### Management modes

- `independent`: the service manages its identity outside Mainstay.
- `mainstay-managed`: Mainstay generated or retains the deployment context for
  the service key and may commission it.
- `self-managed`: used by the Mainstay installation identity when the
  installation is its own immediate authority.

Mainstay uses one installation key as both its installation authority and
control-plane identity because those roles share one custody and rotation
boundary. A higher authority may attest that identity later.

## HTTP Service Contract

Every HTTP service provides a cheap, side-effect-free `/health` response:

```json
{
  "status": "ok",
  "service": "grove",
  "version": "0.1.0"
}
```

Health means that the process can serve requests and its required local state
was initialized. It does not imply commissioning, external reachability,
treasury authority, sufficient wallet reserve or end-to-end payment success.

An information surface returns the product name, version, description,
capabilities and public identity envelope when applicable. Content negotiation
may return a browser-facing page for `Accept: text/html` and JSON otherwise.

Browser-facing links and asset references should be document-relative where
the service may be mounted below a reverse-proxy prefix. Protocol URLs remain
canonical protocol paths.

Public responses use safe defaults appropriate to the protocol, including
`X-Content-Type-Options: nosniff` and explicit cache behavior. CORS is enabled
only to the extent required by the protocol. Operator APIs remain separately
authenticated and more tightly reachable than public information APIs.

## Configuration and Persistence

Environment variables use a component prefix (`CLEAR_`, `GROVE_`,
`SPURLINE_`, `SAFEBOX_`, or `MAINSTAY_`). Repositories provide an annotated
`.env.example` when they have a standalone runtime configuration.

Secrets are generated with cryptographic randomness, stored with restrictive
permissions and never printed. Persistent state records its expected public
service identity. Supplying a different key to existing state causes startup
to fail rather than silently changing the service identity.

Bind-mounted installations retain an atomic mode-`0600` `.env.recovery` at the
instance root, outside every service mount. Updating it must refuse any mismatch
in identity-bound material. It is a convenient same-disk recovery companion,
not a substitute for encrypted off-host secret and data backups.

Recovery is an attachment operation, not bootstrap. `recover-mainstay.sh`
requires the existing data root and its `.env.recovery`, refuses to generate
missing secrets, and verifies that no competing Compose project is attached.
The data-directory name and Compose project name are independent runtime facts:
the operator may reuse the directory basename, explicitly accept a different
Compose name, or abort to rename or remount storage while all services are
stopped. Recovery never performs that filesystem or ZFS rename itself.

Configuration distinguishes:

- human-facing instance presentation, including `MAINSTAY_INSTANCE_NAME`;
- secrets and identity-bound recovery material;
- durable policy and canonical identifiers;
- replaceable internal, local, external and FIPS reachability; and
- development conveniences that must not become production assumptions.

## Python and Repository Convention

Python family repositories use Poetry, commit `poetry.lock`, support Python
3.11 through the current agreed upper bound, expose intentional console entry
points, and separate main, test and documentation dependencies. Tests run from
`tests/`. New service code uses Ruff's import, correctness and modernization
checks where the repository has adopted Ruff; adding a tool to older large
repositories is a separate cleanup change rather than hidden feature work.

README files include purpose, boundaries, development commands, container
operation when applicable, security status and links to deeper design notes.
Generated caches and test output are not source artifacts.

## Container Convention

Runtime images:

- use a multi-stage build where dependencies warrant it;
- pin the Poetry version used during builds;
- run as a non-root service user;
- set `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUNBUFFERED=1`;
- install CA certificates when outbound TLS is possible;
- declare a health check;
- place mutable state in an explicit volume or bind mount;
- use a read-only root filesystem and `no-new-privileges` in Mainstay Compose;
- run one process where SQLite ownership or in-memory subscriptions require a
  singleton; and
- avoid publishing infrastructure ports to the host by default.

`expose` documents an internal Compose-network interface. `ports` publishes a
container interface on the host and therefore requires an explicit local,
VPN, firewall or reverse-proxy boundary.

## Deployment and Update Convention

Addressable applications and services use the same operator-facing lifecycle,
even when their internal configuration differs:

```text
install -> configure -> start -> verify -> update -> back up / recover -> retire
```

A standalone source deployment uses one dedicated checkout or release
directory for one running instance. That directory owns its `.env`, Compose
project and update path. Persistent data and identity-bound secrets must remain
outside the image and survive container replacement.

Documentation should provide one obvious command or short sequence for each
applicable lifecycle step. Use these shared meanings:

- **install** obtains a reviewed source revision or release;
- **configure** selects persistent storage, stable identity, secrets, public
  routes and exposure before first stateful start;
- **start** validates configuration and starts or recreates the intended
  processes without commissioning them implicitly;
- **verify** reports process health separately from identity, commissioning,
  funding and policy readiness;
- **update** advances to a reviewed revision, validates Compose, rebuilds or
  pulls the image, recreates the service and waits for health;
- **back up and recover** preserves matching data, identity-bound secrets,
  policy and the deployed source or image revision; and
- **retire** is an explicit operation distinct from stopping a process or
  replacing a container.

Standalone source checkouts use `./refresh-containers.sh` where supplied. The
script must refuse tracked working-tree changes, use `git pull --ff-only`, run
`docker compose config --quiet`, recreate the intended service set, wait for
the service health contract and print focused status and recent logs on
failure. It does not perform schema rollback, secret rotation, commissioning,
treasury enablement or destructive data cleanup.

The default published bind address is loopback. An operator may deliberately
select a LAN, VPN or reverse-proxy interface and then owns the corresponding
firewall and TLS boundary. Mainstay-managed services are installed and updated
through the Mainstay deployment directory; their standalone refresh scripts
must not be run against the Mainstay-managed containers or data.

Embedded components are installed rather than deployed. An application pins a
reviewed Acorn or Stroma tag or commit in its dependency lock, runs the
component's compatibility and application tests, and commits the resulting
lock change before deployment. Updating an embedded library must not silently
create a new long-running service or service identity.

## Mainstay First-Start Contract

The complete install, recovery and teardown contract is maintained in
[Mainstay Instance Lifecycle and Recovery](MAINSTAY-INSTANCE-LIFECYCLE.md).

A deployment directory owns exactly one Mainstay instance. Its `.env`, Compose
project lifecycle, generated installation identity and teardown authority must
not be shared with another instance. Operators create a separate checkout or
deployment directory for every instance, even when the instances run on the
same host. Each directory also uses a unique `COMPOSE_PROJECT_NAME` so Docker
resources remain instance-scoped. Locally built image tags derive from that
project name as well. This prevents one Mainstay refresh from retagging the
image used by another Mainstay or independently deployed service; Docker may
still deduplicate identical layers beneath those distinct tags.

The instance's human-facing name is independent of those runtime identifiers.
`MAINSTAY_INSTANCE_NAME` supplies the dashboard label and may contain a
community, venue or facility name such as `Cedar Resort`. Mainstay also passes
it to Safebox for instance-scoped availability labels; changing it must not
rename Docker resources, storage paths or service identities.

A fresh interactive installation has one canonical entry point:

```bash
./install-mainstay.sh
```

It must:

1. verify required host commands;
2. show `.env` values as prompt defaults when present and code defaults when
   absent;
3. allow the operator to abort before any mutation;
4. perform read-only checks for required commands, Docker availability, a
   unique Compose namespace, writable storage and available exposed ports;
5. derive an instance-specific data root beneath the selected parent using the
   Compose project name, then review it with the exposed addresses and ports;
6. derive deployment-specific image tags while preserving explicit custom
   image overrides;
7. create or complete `.env` without replacing secrets bound to existing data;
8. establish `MAINSTAY_DATA_ROOT` before first stateful startup;
9. delegate startup to `start-mainstay.sh`, which validates Compose, starts the
   bundle and waits for the control plane, managed services and service Acorn
   worker; and
10. fail with focused status and logs when readiness is not reached.

Routine starts use `./start-mainstay.sh`. Disposable installations use a
dedicated, installer-marked instance root beneath an operator-selected parent.
`./teardown-mainstay.sh` requires an explicit destructive confirmation, removes
Compose volumes and generated configuration, and recursively deletes only an
instance root bearing that marker. It preserves the shared parent, unmarked
operator-owned storage and, by default, built images. The optional
`--remove-images` flag removes only exact project-derived tags and preserves
custom image overrides.

Starting services is not commissioning them, opening Clear treasury authority,
funding the service Acorn, configuring public federation routes, terminating
TLS or proving that backups can be restored. Those remain explicit operator
milestones because they carry policy or value consequences.

## Audit

### Current conformance

| Repository | Conformance | Adjustments in this audit | Deferred work |
| --- | --- | --- | --- |
| Mainstay | Strong control-plane, endpoint-scope, identity and Compose model | Canonical first-start command; standard health envelope; this standard and audit | Automated commissioning/readiness workflow; internal reserve status without Docker control |
| Clear | Reference implementation for identity persistence and commissioning | Standard health envelope; management, state and operator on runtime page; relative runtime links | Production security review and additional governance profiles |
| Grove | Strong independent service boundary and persistent service identity | Standard health envelope; management and state on runtime page; relative runtime links | Commissioning request, attestation and descriptor support |
| Spurline | Strong relay boundary and persistent service identity | Runtime identity management/state display and relative links; health already conforms | Commissioning request, attestation and descriptor support |
| Safebox Web | Strong human app, security boundary and local-first integration | Standard health envelope; distinct persistent application-service identity and information envelope | Commissioning request, attestation and descriptor support |
| Safebox Acorn | Strong protocol and authority boundary | No runtime-service changes apply | Continue release hardening and staged Stroma migration |
| Stroma | Strong narrow protocol boundary and shared FIPS derivation | No runtime-service changes apply | Continue protocol hardening; no service identity is required for the library |
| OpenETR | Strong evidence, consequential-state and recognition boundaries | Adjacent family scope is explicit; voice, multi-stage container and standalone lifecycle now follow the shared conventions | Continue verifier, retrieval, policy-adapter and domain-profile hardening |

### Findings retained as explicit gaps

1. Grove and Spurline possess stable service identities but cannot yet complete
   the Mainstay commissioning exchange implemented by Clear.
2. Safebox Web now has a distinct application-service identity. It remains
   deliberately separate from every user Acorn and from the provider service
   Acorn; its future protocol role and commissioning evidence remain unresolved.
3. Mainstay cannot yet read a live service-Acorn reserve without briefly
   pausing the worker. A future private status interface should report only a
   bounded operational snapshot and never wallet proofs.
4. Production deployments still require explicit choices for storage, pinned
   image revisions, TLS, reverse-proxy trust, federation relays, Clear public
   reachability, commissioning, treasury enablement, reserve funding and
   tested recovery.
5. Visual styles share structure but remain copied into each documentation or
   runtime surface. A shared package would reduce duplication but would also
   couple independent services at runtime; keep the copies until maintenance
   cost justifies a versioned static design package.
6. OpenETR is adjacent to the Mainstay runtime family rather than a default
   managed service. Its protocol and evidence model are shared where useful,
   but deployment and product claims remain independently scoped.

## Review Checklist

For a new family component, ask:

- Is it an app, addressable service or embedded protocol component?
- Is its responsibility and non-responsibility stated plainly?
- Does it use the common product-page anatomy while retaining its own palette?
- Does its voice emphasize ordinary usefulness, shared governance and
  cooperative independence without adversarial or catastrophic framing?
- Does every long identifier wrap on mobile?
- If addressable, does it expose health and non-secret information surfaces?
- Does it need its own service identity, or would that confuse a library with a
  deployed service?
- Are bootstrap, commissioning and operational readiness separate?
- Are endpoint scopes replaceable without changing stable identity?
- Are secrets absent from responses, logs and dashboards?
- Does existing persistent state reject accidental identity replacement?
- Can a fresh operator start it from documented configuration?
- Does its update path require a clean tree, fast-forward source update,
  configuration validation, recreation and a health check?
- Does **availability** describe authorized practical use while
  **reachability** is reserved for a specific network path?
- Are standalone and Mainstay-managed lifecycle ownership kept distinct?
- Does the container run non-root with explicit state and exposure boundaries?
- Are tests proportional to the authority, funds and recovery paths changed?
