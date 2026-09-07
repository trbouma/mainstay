# Service Identity and Operator Attestation

## Status

This note defines the identity roles, evidence chain, lifecycle, and first
implementation sequence for stable Mainstay service identities and operator
attestations. The Clear-first profile is implemented for local testing. Its
NIP-78 event kinds and schemas remain provisional and are not presented as an
interoperable Nostr standard.

This note specializes the broader
[Identity, Resolution, and Event-Native Services](IDENTITY-RESOLUTION-AND-EVENT-NATIVE-SERVICES.md)
design. The broader note explains why identity must be independent of routes;
this note defines how a service and operator prove their relationship.

## Decision Summary

The proposed first profile is:

1. Every independently addressable service has a dedicated Nostr keypair.
2. The service `npub` is its stable identity across Docker, jails, DNS, VPN,
   relay, and FIPS routes.
3. The operator has a separate `npub`; services never receive the operator
   `nsec`.
4. Bootstrap proves possession of the service key but leaves the service
   uncommissioned.
5. Commissioning produces reciprocal evidence: a service-signed request and
   an operator-signed attestation that references it.
6. A service-signed descriptor references the accepted operator attestation.
7. Verification uses signed events, not an unsigned `operator_npub` field.
8. A Mainstay installation acts as the operator authority for services it
   manages and may itself be authorized by a higher authority.
9. The first release supports one directly attesting Mainstay installation per
   service. Multi-operator policy remains a compatible future extension.

The resulting evidence answers three different questions:

```text
service signature
    -> does this process control the service identity?

operator signature
    -> did this operator authorize this service identity and role?

local trust policy
    -> does this verifier recognize that operator as authoritative?
```

No one signature answers all three questions.

## Terminology

### Service identity

A dedicated Nostr keypair for one independently addressable service role. The
public identity is displayed as an `npub`; signed events use the corresponding
32-byte hexadecimal public key required by Nostr.

A service identity identifies the logical service instance, not its URL,
container, host, operator, software package, or legal owner.

### Operator identity

A Nostr keypair representing the person, organization, or governance role that
commissions and authorizes a service. The first profile should prefer a role
identity controlled under an operator policy over a person's everyday social
identity.

### Mainstay installation identity

An optional future keypair representing one Mainstay deployment. It can sign a
deployment manifest and make routine statements about services in that
installation after an operator commissions it.

The Mainstay-managed profile uses the installation as the immediate operator
authority:

```text
Mainstay installation npub --attests--> service npub
```

An autonomous installation treats that `npub` as its local trust root. The
extensible form adds a higher authority without removing local operation:

```text
operator npub --commissions--> installation npub
installation npub --operates--> service npub
```

### Attestation

A signed statement by an authority about another identity. In this profile,
the operator attests that a specific service public key is authorized to act
as a named service type under a defined management relationship.

### Controlling ownership

Cryptographic evidence can prove control of keys and agreement to an
operational relationship. It does not, by itself, prove corporate title,
contractual ownership, regulatory status, or a real-world identity.

Mainstay should therefore describe the claim as `operates`, `authorizes`, or
`controls` unless separate legal credentials support a stronger meaning.

## Identity Boundaries

The initial Mainstay deployment contains these distinct identities:

| Component | Identity | Notes |
| --- | --- | --- |
| Mainstay control plane | Mainstay service or installation `npub` | Coordinates the deployment |
| Spurline | Relay service `npub` | Identifies the relay, not every user publishing to it |
| Grove | Storage service `npub` | Signs descriptors and service evidence |
| Safebox Web | Application service `npub` | Distinct from every hosted Acorn |
| Safebox service Acorn | Provider Acorn `npub` | Existing payment-provider identity |
| Clear | Mint-service `npub` | Distinct from keyset IDs and currency authority |
| Operator | Operator `npub` | Commissions services; private key remains separate |

The Safebox Web identity must not replace a user's Acorn identity or the
service Acorn. The Clear identity must not replace the complete Cashu keyset
ID, CMU, root authority, or treasurer identities. Those objects have separate
authority and rotation rules.

One process may host several logical services only if sharing one service key
matches their custody, authorization, and rotation boundary. A future Clear
process serving independently governed currencies may require one identity per
currency service rather than one identity for the whole process.

## Key Custody

### Managed service keys

For the initial Docker profile, Mainstay bootstrap may generate and preserve:

```dotenv
MAINSTAY_SERVICE_NSEC=
MAINSTAY_INSTALLATION_NSEC=
SPURLINE_SERVICE_NSEC=
GROVE_SERVICE_NSEC=
SAFEBOX_WEB_SERVICE_NSEC=
CLEAR_MINT_SERVICE_NSEC=
```

Each service `nsec` is injected only into its corresponding service.
`MAINSTAY_INSTALLATION_NSEC` is held by the host-side commissioning CLI and is
never injected into a managed service or the long-running control-plane
container. A future higher-authority `nsec` likewise remains outside Mainstay;
only its signed delegation and public key enter the installation.

The `.env` approach is an initial custody mechanism, not the final design.
Service-specific secret files, delegated signers, hardware-backed keys, or a
secret manager should be supported later without changing public identities or
event schemas.

### Persistent identity sentinel

Every service records its derived public key in its own persistent state. On
startup it applies this rule:

```text
configured nsec derives recorded npub
    -> start

no nsec and no persistent service state
    -> remain explicitly unconfigured, or allow the bootstrap helper to create one

persistent state with missing or different nsec
    -> refuse startup and require recovery or explicit rotation
```

Editing `.env` must never silently rotate an existing service. The recorded
`npub` is the mismatch sentinel, while signed continuity evidence provides the
public rotation history.

### Independently deployed services

An independently deployed service follows the same identity contract but owns
its own key custody. Mainstay records only its `npub`, signed evidence, and
verified routes. Adoption into Mainstay management must be explicit and must
not generate a replacement identity merely because Mainstay starts managing
the process.

## Lifecycle State Machine

Services expose one of these identity states:

```text
unconfigured
    -> bootstrapped
    -> commissioning-pending
    -> commissioned
    -> suspended
    -> retired
```

- `unconfigured`: no service key is available.
- `bootstrapped`: the service controls a key and can self-sign, but no trusted
  operator relationship has been established.
- `commissioning-pending`: a service-signed commissioning request exists.
- `commissioned`: a valid operator attestation matches the current service
  identity, role, and commissioning request.
- `suspended`: local policy temporarily refuses the relationship without
  declaring the identity permanently retired.
- `retired`: continuity or revocation evidence says the identity must no
  longer be used for new operations.

An uncommissioned service may remain usable for disposable development. Its UI
and API must not imply operator verification.

## Evidence Chain

### Why reciprocal evidence is required

An operator can sign a statement naming any public key. That proves control of
the operator key and authorship of the statement, but it does not prove that
the named service controls its key or accepts the relationship.

Conversely, a service can claim any operator in an unsigned field or
self-signed descriptor. That does not prove the operator agreed.

The commissioned relationship therefore uses three events:

```text
service commissioning request
    signed by service key
        |
        v
operator attestation
    signed by operator key and references request
        |
        v
service descriptor
    signed by service key and references attestation
```

The first two events are the minimum reciprocal proof. The descriptor makes
the accepted relationship discoverable with current capabilities and routes.

### Service commissioning request

The request is signed by the service key and contains:

```json
{
  "schema": "org.mainstay.service-commissioning-request",
  "schema_version": 1,
  "service": {
    "pubkey": "<service-hex-pubkey>",
    "type": "clear-mint"
  },
  "requested_operator": "<operator-hex-pubkey>",
  "management": "mainstay-managed",
  "nonce": "<random-256-bit-value>",
  "issued_at": 1788700000,
  "expires_at": 1788786400
}
```

Required event tags should include:

```text
["d", "org.mainstay.service-commissioning-request:<nonce>"]
["p", "<operator-hex-pubkey>", "", "operator"]
["t", "mainstay-service-commissioning"]
["service-type", "clear-mint"]
["expiration", "1788786400"]
```

The event author must equal `service.pubkey`. The nonce prevents a stale
operator signature from being applied to a new request, while expiry limits
the useful life of an unattended request.

### Operator attestation

The attestation is signed by the operator key and contains:

```json
{
  "schema": "org.mainstay.service-operator-attestation",
  "schema_version": 1,
  "action": "authorize",
  "service": {
    "pubkey": "<service-hex-pubkey>",
    "type": "clear-mint"
  },
  "relationship": "operates",
  "management": "mainstay-managed",
  "commissioning_request": "<request-event-id>",
  "installation": "<mainstay-installation-hex-pubkey>",
  "sequence": 1,
  "previous": null,
  "issued_at": 1788700100
}
```

Required event tags should include:

```text
["d", "org.mainstay.service-operator-attestation:<service-hex-pubkey>"]
["p", "<service-hex-pubkey>", "", "service"]
["e", "<request-event-id>", "", "commissioning-request"]
["t", "mainstay-service-operator"]
["service-type", "clear-mint"]
```

The event author is the operator public key and is the authoritative source of
`operator_npub`; the content must not name a conflicting operator. The
attestation references the exact service-signed request, including its nonce,
role, and requested operator.

### Service descriptor acceptance

The next service-signed descriptor references the attestation:

```json
{
  "schema": "org.mainstay.service-descriptor",
  "schema_version": 1,
  "service": {
    "pubkey": "<service-hex-pubkey>",
    "type": "clear-mint"
  },
  "operator": {
    "pubkey": "<operator-hex-pubkey>",
    "attestation_event_id": "<attestation-event-id>"
  },
  "management": "mainstay-managed",
  "capabilities": ["cashu.info", "cashu.keys", "clear.mint"],
  "issued_at": 1788700200,
  "state": "commissioned"
}
```

Required event tags should include:

```text
["d", "org.mainstay.service-descriptor"]
["p", "<operator-hex-pubkey>", "", "operator"]
["e", "<attestation-event-id>", "", "operator-attestation"]
["t", "mainstay-service-descriptor"]
["service-type", "clear-mint"]
```

The descriptor does not make the operator claim true. It proves that the
service accepted and is currently advertising the referenced relationship.
Endpoint advertisements, expiry, replacement sequencing, and revocation are
deliberately deferred until their lifecycle rules are implemented and tested.

### Event kinds

The Clear-first experiment uses NIP-78 application-specific data events:

- kind `78` for an immutable commissioning request; and
- kind `30078` for the current operator attestation and service descriptor,
  distinguished by their `d` tags.

These assignments are provisional. They intentionally use the existing
application-data envelope while the schemas are local to Mainstay. A future
interoperability proposal may assign dedicated kinds after reviewing collision
risk, replacement semantics, deletion behavior, and relay support.

Event validity never depends on relay publication. A complete signed event can
be verified from a file, QR transfer, local registry, removable media, or FIPS
transport. Relays provide discovery and availability.

## Verification Algorithm

A verifier evaluates a commissioned service as follows:

1. Decode every event and recompute its Nostr event ID.
2. Verify every Schnorr signature.
3. Confirm the commissioning-request author equals the service public key.
4. Confirm the requested operator equals the attestation author.
5. Confirm the attestation references the exact request event ID.
6. Confirm service public key, service type, management mode, and optional
   installation are identical across the request and attestation.
7. Confirm the descriptor author equals the service public key and references
   the exact attestation event ID.
8. Validate issue time, expiry, sequence, predecessor, and revocation state.
9. Apply local policy to decide whether the operator public key is trusted for
   this service type and deployment.
10. Validate domain-specific bindings, such as Clear root authorization of a
    mint-service identity or a keyset-to-service record.

Successful cryptographic verification produces evidence such as:

```yaml
service_key_control: verified
operator_authorship: verified
reciprocal_relationship: verified
operator_trust: trusted-by-local-policy
domain_authority: verified
```

The API should preserve these distinctions rather than collapse them into one
ambiguous `verified: true` value.

## Public Service Response

Each service should expose a bounded identity summary from its existing info or
homepage response:

```json
{
  "service_identity": {
    "npub": "npub1service...",
    "type": "clear-mint",
    "management": "mainstay-managed",
    "state": "commissioned",
    "descriptor_event_id": "<event-id>",
    "operator": {
      "npub": "npub1operator...",
      "attestation_event_id": "<event-id>",
      "status": "verified"
    }
  }
}
```

No endpoint returns an `nsec`, commissioning nonce after use, or unrestricted
internal topology. A separate evidence endpoint may return complete signed
public events needed for offline verification. The path is a compatibility
surface, not part of the identity.

Mainstay's dashboard may display the service and operator `npub`s plus evidence
state. It must distinguish:

- self-controlled but uncommissioned;
- operator attestation present but not verified;
- cryptographically verified but operator not trusted locally;
- fully commissioned under local policy; and
- expired, revoked, mismatched, or rotated evidence.

## Bootstrap Flow

For a new Mainstay deployment:

```text
init-env
    -> generate missing managed service keys
    -> never print private keys
    -> refuse replacement over existing service state

service startup
    -> derive npub
    -> compare with persistent identity sentinel
    -> expose bootstrapped/uncommissioned identity

mainstay identity requests create
    -> collect service-signed commissioning requests
    -> export a bounded commissioning bundle
```

The bootstrap helper does not hold the operator key and cannot commission the
services by itself.

## Commissioning Flow

The implemented Clear-first workflow is:

```bash
./init-env.sh
poetry run mainstay-local service commission clear
poetry run mainstay-local service show clear
poetry run mainstay-local service verify clear
```

`service commission clear` asks Clear to sign a request, verifies it, signs the
operator attestation with the Mainstay installation key, returns it to Clear,
asks Clear to verify and retain the complete evidence chain, and publishes the
three public events through Clear to internal Spurline. `--no-publish` retains
the evidence locally when the relay is intentionally unavailable.

The command accepts the managed registry name `clear`, not an arbitrary URL or
service `npub`. The workflow requirements are:

- show the operator every service `npub`, type, installation, and management
  mode before signing;
- reject unknown, duplicated, expired, or mismatched requests;
- import only complete signed events;
- verify before mutating commissioned state;
- retain the evidence after commissioning; and
- produce an operator-readable verification report.

Online relay publication can be an additional command. Offline commissioning
must remain possible.

## Rotation, Revocation, and Recovery

### Planned service rotation

A planned rotation requires:

1. the old service signs a successor event naming the new service key;
2. the new service signs an acceptance event naming the old key;
3. the operator attests the new service key and references the continuity
   evidence;
4. the service publishes a new descriptor; and
5. Mainstay retains the old identity and evidence as retired history.

Rotation of a service communication key does not rotate user Acorns, Clear
keysets, CMUs, currency roots, content hashes, or unrelated service keys.

### Operator replacement

Changing operators requires a new service request, a new operator attestation,
and a service descriptor accepting it. When possible, the old operator should
sign a transfer or revocation statement. Local governance policy determines
whether a new operator can replace an unavailable old operator.

### Revocation

The operator can publish an immutable revocation statement referencing the
active attestation. The service can also publish a descriptor that withdraws
the relationship. Verifiers apply the strongest relevant evidence available
under local policy and preserve the prior events for audit.

An addressable replacement event alone is not sufficient revocation evidence
because relays can omit history. The event schema must support an explicit,
independently retained revocation record.

### Key loss

Loss of the service key prevents dual-signed continuity. Recovery relies on a
previously trusted operator or domain authority and must be shown as recovery,
not equivalent to planned rotation. Loss of the operator key requires the
operator's own pre-established governance or recovery policy; services must
not silently accept a newly configured operator `npub`.

## Threat Model

### Service key compromise

An attacker can impersonate the service and sign descriptors, but cannot
produce a new trusted operator attestation. Verifiers should reject unapproved
role changes and routes that are inconsistent with the last valid authority
evidence.

### Operator key compromise

An attacker can attest new services or revoke relationships. Reciprocal
service evidence prevents the attacker from proving control of an existing
service key, but operator compromise remains a governance emergency. Future
profiles should support threshold or delegated operator policy.

### Shared `.env` compromise

An attacker may obtain several service keys at once. Separation by identity
still helps verification and rotation, but it is not custody isolation. This
risk motivates per-service secret mounts or external signers.

### Replay and rollback

Nonce, expiry, sequence, predecessor, and explicit revocation checks prevent a
stale commissioning bundle or descriptor from silently replacing newer
evidence. Offline policy may temporarily accept cached evidence but must report
its age and inability to check newer revocations.

### Relay censorship or substitution

Relays can hide evidence or serve stale events but cannot forge signatures.
Mainstay should query more than one configured source when online and retain
the last verified evidence locally. A relay URL is not an authority.

### Endpoint substitution

A valid operator relationship does not make every advertised endpoint safe.
Clients must verify the service-signed descriptor, scope, capability, and any
domain-specific route binding before use.

## FIPS Relationship

The service `npub` remains stable when FIPS is introduced. FIPS supplies a
deterministic identity-derived network route; it does not replace operator
commissioning or service descriptors.

When a service uses a distinct FIPS node identity, the service-signed
descriptor binds:

```text
service npub
    -> FIPS node npub
    -> application port and capability
```

The operator attestation authorizes the service identity and role. The
service-signed descriptor advertises current FIPS reachability. This keeps
governance, service identity, and network transport as separate layers.

## First Implementation Sequence

### Phase 1: Shared contract

- Freeze schema names and canonical JSON rules.
- Select Nostr event kinds after interoperability review.
- Create cross-repository valid and invalid event fixtures.
- Implement one verifier with identical behavior across services.

### Phase 2: Service bootstrap

- Extend `init-env.sh` to generate Mainstay, Spurline, Grove, and Safebox Web
  service keys as it already does for Clear.
- Inject each key only into its service.
- Add persistent `npub` sentinels and mismatch refusal to each service.
- Expose uncommissioned identity summaries without private material.

### Phase 3: Direct operator commissioning

- Generate one `MAINSTAY_INSTALLATION_NSEC` and record its derived public
  identity sentinel.
- Generate service-signed commissioning requests.
- Add offline export, signing, import, and verification workflows.
- Store complete signed evidence and show its state in the dashboard.

### Phase 4: Discovery and publication

- Publish audience-appropriate descriptors and attestations to configured
  relays.
- Add relay-backed resolution and local evidence caching.
- Keep internal routes out of public descriptor projections.

### Phase 5: Installation and FIPS profiles

- Add an optional Mainstay installation identity and signed deployment
  manifest.
- Define delegated authority from operator to installation.
- Bind service identities to FIPS node identities and capabilities.
- Add continuity, revocation, and multi-operator governance profiles.

Clear is the existing reference implementation for service-key generation,
public identity reporting, and persistent identity mismatch detection. Its
operator attestation should be added through the shared contract rather than a
Clear-specific event format.

## Open Questions

1. Should dedicated interoperable event kinds eventually replace the
   provisional NIP-78 application-data profile?
2. Should a later operator attestation expire, or remain valid until explicit
   revocation with a recommended renewal interval? The first profile remains
   valid until explicit replacement or revocation.
3. Is `operates` the correct relationship term, or do deployments need
   separate `owns`, `hosts`, `administers`, and `authorizes` claims?
4. Should the first profile allow one operator per service only, or model a
   list while enforcing threshold one?
5. Which service state stores complete evidence, and which evidence belongs in
   a shared Mainstay registry cache?
6. Should Mainstay itself first receive a service identity, an installation
   identity, or both?
7. How should an operator signer establish its human-readable identity without
   making DNS or NIP-05 authoritative?
8. What bounded offline policy is acceptable when current revocation evidence
   cannot be queried?
9. Which Clear authority must additionally attest a mint-service identity for
   commissioned CMUs and keysets?
10. Should a Safebox Web service identity attest its provider Acorn
    relationship, or should the operator attest both identities independently?
11. How should public and local descriptor projections prove that they belong
    to the same service without leaking internal topology?
12. What backup and recovery evidence is required before Mainstay offers
    automated key rotation?

## Acceptance Criteria for the First Profile

The first profile is complete when:

- every managed addressable service has a unique, persistent `npub`;
- replacing or removing a configured service key over existing state prevents
  normal startup;
- no service, log, registry response, or dashboard exposes an `nsec`;
- the operator key remains outside service containers;
- every commissioned service has a valid reciprocal request-attestation chain;
- an offline verifier can validate that chain from exported signed events;
- the dashboard distinguishes possession, attestation, trust, and
  domain-authority status;
- rotation and revocation evidence cannot silently change unrelated stable
  identities; and
- the same service identity remains valid as routes move from Docker to local,
  external, or FIPS reachability.
