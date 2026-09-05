# Mainstay Identity, Resolution, and Event-Native Services

## Status

This is an exploratory design note. It establishes architectural boundaries
and a direction for incremental experiments; it does not assign final Nostr
event kinds, replace existing HTTP APIs, or require every Mainstay interaction
to become a durable event.

The companion [address-space note](ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md)
defines internal, local, and external endpoint scopes. This note defines the
identity and protocol layers above those routes.

The design can be summarized in five steps:

> Resolve the identity. Discover the capability. Send the message. Choose the
> transport. Verify the evidence.

## Purpose

Mainstay needs a unified model for service identity, resolution, discovery,
messaging, transport, and evidence. The immediate motivation is practical:
Docker names, LAN addresses, VPN routes, public domains, and future FIPS paths
may all reach the same service. Comparing those locations cannot reliably
answer whether two clients use the same service.

The proposed direction is:

> Every independently addressable Mainstay service has a cryptographic
> identity independent of its network location.

The default representation of that identity is a Nostr public key, displayed
as an `npub`. URLs, ports, REST paths, containers, jails, and FIPS locators are
attributes or routes associated with the service. They are not its identity.

The long-term proposition is that Mainstay services become npub-addressed,
capability-described, event-native, and transport-independent while retaining
REST and HTTP as compatibility interfaces.

## Architectural Invariants

The following are proposed invariants rather than experimental details:

1. A network location is not a durable service identity.
2. Every independently addressable service has its own service identity.
3. An operator identity and a service identity are distinct roles, even when
   one person initially controls both keys.
4. A stable domain identifier such as a Cashu keyset ID is not automatically a
   service identity.
5. Resolution answers which identity is responsible for an identifier.
6. Discovery answers what an identified service can do and how it can be
   reached.
7. Capabilities describe protocol meaning; paths describe one way to invoke
   that meaning.
8. Transport must not change the semantic meaning of a protocol operation.
9. Authentication proves control of a key; authorization determines what that
   identity is permitted to do.
10. Consequential state should be supported by end-verifiable evidence rather
    than asserted only by an application database.
11. Mainstay must not claim that an HTTP client signed a request when only a
    compatibility gateway signed an internal representation of it.
12. Key rotation and service replacement must be explicit continuity events,
    not silent edits to a registry.
13. Mainstay manages private keys only for services it operates. It verifies
    externally managed identities without taking custody of their keys.

## Identity Roles

### Operator and installation

An operator `npub` identifies a person or governance role that commissions and
authorizes services. A future Mainstay installation `npub` may sign the local
deployment manifest and attest which service identities belong to that
installation.

```text
operator npub
    |
    +-- commissions --> Mainstay installation npub
                            |
                            +-- operates --> Spurline service npub
                            +-- operates --> Grove service npub
                            +-- operates --> Safebox Web service npub
                            +-- operates --> Clear service npub
```

Possession of a service key does not prove that a recognized operator
commissioned it. A self-signed descriptor proves control and continuity of the
service identity; an operator or installation attestation establishes its
place in a deployment or governance domain.

### Service instances and roles

An independently addressable service receives a dedicated keypair when it must
receive private messages, sign responses, advertise capabilities, or be
distinguished from another instance of the same software.

Initial candidates include:

- Spurline relay instances;
- Grove storage instances;
- Spruce services when independently deployed;
- Safebox Web instances;
- Safebox payment-provider workers;
- Clear mint or currency-service instances; and
- future independently addressable Mainstay services.

One process does not necessarily equal one identity. A process hosting several
independent currency services may need a service identity for each separately
authorized currency. Conversely, helper processes implementing one logical
service may share that service's public identity only when the private-key
custody and authorization boundary permit it.

Safebox Web and its service Acorn illustrate the distinction. The existing
service Acorn `npub` identifies the payment-provider role. It should not
silently become the identity of the entire Safebox Web application if those
roles need different authority, lifecycle, or compromise boundaries.

### Identity management modes

Mainstay should record how each service identity is managed:

| Mode | Private-key custody | Mainstay responsibility |
| --- | --- | --- |
| `managed` | Mainstay deployment | Generate, inject, back up, verify, and rotate |
| `external` | Independent service operator | Pin identity, verify evidence and descriptors, and select routes |
| `compatibility` | Unknown or not provided | Route by URL with explicitly reduced identity assurance |

A managed identity belongs to the service instance operated by that Mainstay
installation. An external identity remains under the independent operator's
control; Mainstay stores its public identity, signed descriptor, authority
evidence, and verified routes but never imports its `nsec`.

A compatibility service remains usable when an existing protocol has no
service-identity mechanism. Mainstay may verify domain-specific facts, such as
the Cashu keyset actually returned by a mint URL, but must not claim that the
URL has been cryptographically bound to a service `npub`.

Moving a service between modes is an explicit adoption or release operation.
Taking an external service under Mainstay management should preserve its
existing identity when secure key transfer is intended and possible. Mainstay
must never generate a replacement merely because it now launches the
container.

### Stable non-service identifiers

Some stable identifiers name domain objects rather than services:

| Identifier | Identifies | Does not identify |
| --- | --- | --- |
| Acorn `npub` | A user or agent | Its current relay or application URL |
| Service `npub` | An addressable service role | Its operator or current host |
| Cashu keyset ID | A public issuance keyset | A URL or all keysets at one mint |
| `cmu-<keyset-id>` | A Clear Mint Unit | A friendly currency name |
| Grove content hash | Immutable blob bytes | The uploader or storage location |
| Nostr event ID | Exact signed event content | The latest state of a replaceable record |

These identifiers can participate in resolution without being collapsed into
one universal identity type.

## Layered Model

```text
+--------------------------------------+
| IDENTIFIER                           |
| human alias / keyset ID / object ID  |
+-------------------+------------------+
                    | resolve
                    v
+--------------------------------------+
| IDENTITY                             |
| service npub                         |
+-------------------+------------------+
                    | describe
                    v
+--------------------------------------+
| CAPABILITY                           |
| protocols / operations / versions   |
+-------------------+------------------+
                    | deliver
                    v
+--------------------------------------+
| TRANSPORT                            |
| FIPS / Nostr relay / HTTP            |
+--------------------------------------+
```

Each boundary should remain independently testable:

- **Identifier:** What am I looking for?
- **Identity:** Which cryptographic service identity is responsible for it?
- **Capability:** What does that service understand?
- **Transport:** How can I reach it from this scope?
- **Evidence:** What proves the result and its authorization?

## Resolution

### Small primitive

The public conceptual operation is deliberately narrow:

```text
resolve(identifier) -> npub
```

It must not become a second general service registry. Resolution maps an
identifier to the cryptographic identity responsible for it. Description and
endpoint selection happen later.

Implementations should retain the evidence behind the answer even if a simple
CLI prints only the resulting `npub`:

```yaml
identifier: 009a...
identity: npub1clearmint...
evidence:
  type: clear-root-service-record
  event_id: 4ab3...
  verified_at: 1788566400
```

A cache entry without its provenance, validity period, and verification result
must not be treated as an authoritative resolution.

### Keyset resolution

The target operation is:

```text
keyset_id -> mint service npub
```

Fetching Cashu keys and reproducing the keyset ID proves that a route serves
the expected public keyset. It does not by itself prove which service identity
is authorized to represent that keyset. Clear should obtain that binding from
the currency root policy or a root-signed service record. A conventional Cashu
mint without such an authority record may remain URL-routed and explicitly
marked as an unbound compatibility service.

For Clear, the following must remain distinct:

```text
currency root identity
    authorizes
mint service npub
    serves
cmu-<keyset-id>
```

A keyset may survive a service-key rotation. The resolver updates the active
service `npub` only after verifying authorized successor evidence; circulating
proofs retain the same keyset identity.

### Human aliases

Aliases such as `clear` or `spurline` should be local to a Mainstay
installation by default:

```text
spurline -> npub1relay...
clear    -> npub1clearmint...
```

Public or cross-installation aliases require an explicit namespace authority
and signed assignment. Mainstay should not recreate DNS by quietly treating a
globally ambiguous string as authoritative.

## Service Discovery

After resolution, discovery retrieves a descriptor signed by the service
identity:

```text
describe(npub) -> verified service descriptor
```

A candidate descriptor is:

```yaml
schema: org.mainstay.service-descriptor
schema_version: 1
service:
  npub: npub1spurline...
  type: nostr-relay
operator:
  npub: npub1operator...
capabilities:
  - name: nostr.relay
    version: 1
  - name: mainstay.service.describe
    version: 1
endpoints:
  - scope: internal
    transport: websocket
    locator:
      url: ws://spurline:8080
  - scope: local
    transport: websocket
    locator:
      url: ws://192.168.1.20:8080
  - scope: external
    transport: fips-native
    locator:
      node_npub: npub1fipsnode...
      port: 8080
relationships:
  installation: npub1mainstay...
issued_at: 1788566400
expires_at: 1791158400
sequence: 4
previous: 7cd2...
```

The descriptor's Nostr event author must match `service.npub`. Consumers must
also validate schema, timestamps, sequence, predecessor rules, endpoint
policy, and any required operator or root attestation.

### Descriptor event kind

No final event kind is assigned by this note. A service descriptor naturally
resembles a NIP-01 addressable event because one service may advertise several
descriptor classes and clients usually need the latest valid version.
Addressable kinds occupy the `30000` through `39999` range and are keyed by
kind, author, and `d` tag. Selecting a concrete kind requires a collision and
interoperability review rather than choosing an attractive unused number in a
local document.

The first experiment may store a complete signed event in Mainstay's local
registry without publishing it to any relay. Relay publication is a transport
and availability choice, not a validity requirement.

### Updates, expiry, and supersession

Descriptors should contain:

- a monotonically increasing sequence within one service identity;
- issue and expiry times;
- the previous descriptor event ID after the first version;
- a stable descriptor class in the `d` tag if an addressable event is used;
- enough endpoint metadata to distinguish scope, transport, purpose, and
  priority; and
- optional operator or authority attestations referenced by event ID.

Consumers reject expired descriptors unless an explicit offline continuity
policy permits a previously verified descriptor. Equal or lower sequence
numbers cannot supersede a verified newer descriptor. Clock skew and offline
operation need bounded, operator-visible policies.

Descriptors also need audience-aware disclosure. An internal endpoint,
operator relationship, or local topology may be appropriate in a descriptor
pinned inside one Mainstay installation but unsafe to publish publicly. A
service should sign separate descriptor classes or projections for local and
public audiences rather than publish one maximal document and expect consumers
to ignore sensitive fields. Every projection still names the same service
identity and must have its own sequence, expiry, and verification state.

## Capabilities Before Paths

Mainstay should ask what a service understands, not begin with its URL layout.
For example:

```text
cashu.info
cashu.keys
cashu.mint.quote
cashu.mint
cashu.melt.quote
cashu.melt
nostr.relay
blossom.put
blossom.get
```

An HTTP binding may map `cashu.keys` to `/v1/keys`; a FIPS or Nostr binding may
carry an event with the same capability name. The capability owns the semantic
contract. The binding owns transport-specific framing.

Capability records should include an integer major version and, where useful,
a schema identifier or digest. A consumer must negotiate a mutually supported
major version before sending a consequential request. Minor compatible
extensions should be optional fields with defined ignore rules.

Paths remain useful descriptor data for HTTP compatibility:

```yaml
capability: cashu.keys
version: 1
bindings:
  - transport: http
    method: GET
    path: /v1/keys
```

They are not copied into the stable service identity.

## Event-Native Protocol Objects

### Request and response

An event-native operation is a signed exchange between identities:

```text
Safebox npub                       Clear service npub
     |                                      |
     +---- MintQuoteRequest --------------->|
     |     signed, correlated, expiring     |
     |                                      |
     |<--- MintQuoteResponse ---------------+
     |     signed, references request       |
```

A protocol event should identify at least:

- sender event author;
- recipient service in a `p` tag;
- capability and major version;
- request or operation identifier;
- creation and expiry time;
- idempotency key where mutation is possible;
- canonical payload or encrypted payload;
- references to the request and prior state where applicable; and
- the NIP-01 event ID and signature.

Responses should be signed by the resolved service identity, address the
requester, reference the exact request event ID, and carry a machine-readable
status. A response from an unexpected key is not made valid by arriving from
the expected URL.

### Correlation, replay, and idempotency

The Nostr event ID identifies the exact signed request but is not sufficient
as a business idempotency rule. A service should persist a bounded operation
key such as:

```text
(sender pubkey, capability, idempotency key)
```

Repeated delivery of the same authorized operation returns the recorded
result. Reuse with different payload content is rejected. Services must check
expiry before execution, impose a maximum request lifetime, and retain replay
records for at least the longest period in which duplicate execution would be
harmful.

Long-running operations may emit accepted, progress, completed, or failed
events that all reference the original request. A transport acknowledgement
means only that bytes or an event were accepted by that transport; it does not
mean the application operation completed.

### Encryption and metadata

Signatures provide attribution and integrity, not confidentiality. Private
application payloads require end-to-end encryption to the recipient service
identity. NIP-44 payload encryption and NIP-59-style wrapping are candidates
for relay delivery, but the final profile must define exactly which event is
signed, which metadata remains visible, and which inner protocol object is
identical across transports.

The preferred abstraction is an immutable signed protocol object with an
optional transport envelope. FIPS may protect the transport end to end, but a
consequential message may still need application-level encryption and a
portable signature so it remains verifiable after leaving the FIPS session.
Transport encryption must not be mistaken for durable application evidence.

### Event kinds

This note does not allocate request and response kinds. The options include:

- regular stored events for evidence that must remain retrievable;
- ephemeral events in the `20000` through `29999` range for transient request
  delivery;
- addressable events for current descriptors; and
- an inner signed protocol object carried inside existing encrypted delivery
  events.

Different operations may need different retention semantics. A single generic
RPC kind is easy to prototype but risks erasing useful validation and
authorization boundaries. The first experiment should define one narrow
capability and measure its behavior before proposing a shared kind family.

## Transport Independence

```text
                 Mainstay protocol
                        |
              signed protocol object
                        |
             +----------+----------+
             |          |          |
             v          v          v
           FIPS     Nostr relays   HTTP
```

The protocol object should retain the same semantic meaning over every
transport. Byte-for-byte identity is possible when the signed object is passed
unchanged inside a transport envelope. It is not possible when a transport
requires mutation of the signed event itself. The experimental protocol must
therefore specify the signed inner object separately from transport metadata.

### FIPS

FIPS uses Nostr keypairs as node identities, derives routing and IPv6 adapter
addresses from the public key, and provides authenticated end-to-end sessions.
Its current IPv6 adapter lets unmodified applications operate through a TUN
interface and local `.fips` resolution. Its native npub-addressed datagram API
is explicitly experimental.

The boundary is:

```text
Mainstay: identity meaning, resolution, capabilities, application semantics,
          authorization, and durable evidence

FIPS:     node reachability, routing, sessions, and network transport
```

In short, Mainstay resolves meaning; FIPS resolves reachability.

Mainstay should not duplicate FIPS routing, peer discovery, session security,
or npub-to-overlay-address preparation. It should supply a verified destination
and application port or use the IPv6 compatibility path.

### Service identity versus FIPS node identity

Whether a service key and FIPS node key should be identical remains an
experimental question. Reusing one key makes direct `service npub:port`
addressing simple, but it also gives the FIPS daemon custody of the service
identity key and couples application-key rotation to network identity.

The safer general model permits distinct keys:

```text
service npub --signed binding--> FIPS node npub + application port
```

A single-service appliance may deliberately use one key only after documenting
the custody and rotation tradeoff. A host-level FIPS node serving several
Mainstay services must use signed bindings because one node `npub` cannot also
be the distinct identity of every application service.

### Nostr relays

Relays can distribute and retain signed protocol objects without becoming
their authority. Relay acceptance is not application acceptance. Sensitive
events should use appropriate encryption and retention controls, and an
operation must remain idempotent when several relays deliver the same event.

### HTTP and REST

REST remains necessary for browsers, Cashu clients, Blossom clients, health
checks, and third-party interoperability. It becomes a compatibility
projection of protocol semantics rather than the source of those semantics:

```text
HTTP request
    -> validate compatibility request
    -> invoke the same capability handler
    -> produce protocol result
    -> project result into HTTP response
```

An authenticated HTTP client may supply evidence that can be bound into the
internal operation. An anonymous or conventionally authenticated Cashu client
does not possess a Nostr signing key merely because the adapter uses signed
objects internally. In that case, the adapter's signature attests that it
received and translated the request; it does not attribute authorship to the
client.

Existing Cashu NUT endpoints and response contracts remain authoritative for
compatibility clients until a separately specified event-native Cashu profile
exists. Mainstay must not introduce semantic differences hidden behind a REST
adapter.

## Evidence and Consequential State

Not every message deserves permanent evidentiary weight. The design separates:

- **ephemeral communication:** presence, probes, progress hints, and retryable
  queries;
- **operational records:** descriptors, acknowledgements, and bounded replay
  records needed to run the service safely; and
- **consequential evidence:** authorized requests, approvals, issuance,
  transfers, acceptance, completion, revocation, and succession records whose
  verification changes rights or obligations.

For consequential operations, the desired chain is:

```text
signed request
    -> signed acceptance
    -> signed completion or failure
    -> independently verifiable resulting state
```

Databases remain necessary indexes, caches, queues, and materialized views.
They should store the evidence from which consequential state can be checked,
not become the only source asserting that the event occurred.

Blockchain inclusion is also not sufficient by itself. It may prove ordering
or settlement but not the complete application meaning, authority, recipient
intent, or service response. Those claims remain in the signed protocol
evidence.

## Key Lifecycle

### Bootstrap and commissioning

Bootstrap creates the technical service identity. Commissioning gives that
identity recognized authority and relationships.

```text
bootstrap
    -> generate or recover service key
    -> derive and record service npub
    -> start in an uncommissioned state

commissioning
    -> bind service npub to operator or Mainstay installation
    -> authorize capabilities and endpoint publication
    -> add domain-specific authority, such as a Clear root service record
```

An uncommissioned identity can prove possession of its key but cannot prove
that a trusted operator, installation, or currency authority recognizes it.

### Generation and initial storage

Mainstay bootstrap should generate a service key only when the corresponding
persistent service state does not already exist. The behavior should mirror
the current refusal to generate a replacement Clear master secret or Safebox
cookie key over an existing data volume.

For an initial Docker implementation:

- managed service `nsec`s may be stored in Mainstay's mode-`0600` `.env` file;
- Compose injects only the relevant `nsec` into each service container;
- Mainstay stores and displays only the `npub` in its ordinary registry;
- backups preserve `.env` and all corresponding service volumes together;
- logs and dashboard responses never expose the `nsec`.

The initial variables may be:

```dotenv
MAINSTAY_SERVICE_NSEC=
SPURLINE_SERVICE_NSEC=
GROVE_SERVICE_NSEC=
SAFEBOX_WEB_SERVICE_NSEC=
CLEAR_MINT_SERVICE_NSEC=
```

`CLEAR_MINT_SERVICE_NSEC` is a provisional name for the first single-currency
experiment. Clear's target model gives each independently authorized currency
service its own identity, so a future multi-currency process will require a
keyed identity store rather than one global environment variable.

The existing Safebox payment-provider Acorn retains its separately managed
identity in Safebox state. Mainstay must not generate a second provider key
under a new environment variable.

An `.env` file is a practical first implementation, not the final custody
boundary. Commands such as `docker compose config` and `docker inspect` can
expose injected values to an authorized local operator, and theft of one file
can compromise several managed services. Later deployments should support
service-specific mounted secret files, a secret manager, hardware-backed
signers, or delegated signing without changing public identities or descriptor
formats.

For every storage mechanism, bootstrap follows the same rule:

```text
configured key derives recorded npub
    -> start normally

no key and no persistent service data
    -> generate a new identity

persistent service data but key missing or different
    -> refuse startup and require recovery or explicit rotation
```

The public `npub` recorded with service state is the mismatch sentinel. Editing
an `nsec` in `.env` must not silently assign a new identity to an existing
service.

### Rotation and continuity

A replacement key creates a new cryptographic identity. Continuity is a
verified relationship, not literal key equality. A planned successor should
be supported by:

1. a final event signed by the old service key naming the new key;
2. an acceptance event signed by the new key;
3. a current operator, installation, or domain-authority attestation; and
4. service-specific authorization, such as a Clear currency-root service
   record.

Emergency replacement after key loss cannot rely on the old key. It requires
the pre-established operator or domain authority and should be visibly weaker
evidence than dual-signed planned rotation.

Rotation of a service communication key must not rotate unrelated identities:
Cashu keysets, Clear currency roots, user Acorns, content hashes, and the
Mainstay installation identity continue according to their own rules.

Rotation should eventually be exposed as a controlled command rather than a
text-editing convention:

```text
mainstay-local identity rotate <service>
mainstay-local identity rotate <service> --dry-run
mainstay-local identity recover <service> --authority-event <file>
```

The normal rotation command should verify current state, stage rather than
overwrite the new key, create old-key succession and new-key acceptance
evidence, obtain required authority, atomically update custody and descriptors,
restart the service, verify the reported `npub`, and retain the retired
identity in history. Recovery without the old key relies on pre-established
operator or domain authority and must be distinguished from dual-signed
planned succession.

Service-specific hooks remain necessary. Clear rotation must update a root-
authorized service binding without changing keysets or `CLEAR_MASTER_SECRET`.
The payment-provider Acorn must use its obligation-draining and migration
workflow rather than a generic service-key command.

### Independently operated services

An independently deployed service generates, stores, backs up, and rotates its
own key. It can provide its signed descriptor through a relay, FIPS, HTTPS, or
an operator-supplied file. Mainstay verifies the signature and required
authority chain, records the service as `external`, and never requests the
private key.

For example:

```yaml
services:
  community_relay:
    management: external
    service_identity: npub1remote...
    descriptor:
      event_id: 4ab3...
      verified: true
    endpoints:
      - scope: external
        transport: websocket
        locator:
          url: wss://relay.example.org
```

If the external service rotates, Mainstay updates the pinned identity only
after validating its succession and authority evidence. An endpoint response
advertising a different `npub` is a mismatch, not an automatic rotation.

## Service-by-Service Application

### Spurline

Spurline remains a useful follow-on experiment. Give the managed relay a
persistent service identity and a signed descriptor containing its internal,
local, external, and FIPS bindings. Mainstay can then map several URLs to one
relay identity.

Safebox's same-relay payment decision should eventually compare:

```text
sender home relay npub == recipient home relay npub
```

The current normalized-URL comparison remains a valid transitional rule only
inside a deployment where both parties use the same canonical Docker URL.

### Grove

Grove can use a service `npub` to sign capability and endpoint descriptors and
future storage receipts. Blob identity remains the content hash; uploader and
owner identities remain their own public keys. Grove's service identity must
not replace either.

### Spruce

If Spruce operates as an independently addressed service, it receives its own
identity and advertises its semantic capabilities. If it is only an embedded
library, it does not need a network service identity merely because its code is
part of Mainstay.

### Safebox Web and service Acorn

Safebox Web may need an application-service identity for descriptors and
application responses. Its payment-provider service Acorn already has a
persistent identity with different authority. These should remain separate
unless a later threat-model review demonstrates that they have the same
addressability, custody, and rotation boundary.

User Acorn `npub`s continue to identify users or agents. A claimed handle,
Lightning address, relay URL, LAN address, or FIPS route is discovery data for
that identity.

### Clear

Clear already anticipates a currency-specific mint-service identity distinct
from the currency root, treasurer identities, and Cashu operational keysets.
The root policy or root-signed service record should bind each keyset and CMU
to the active mint-service identity and endpoints.

The first Mainstay experiment should consume this model rather than introduce
a competing global Clear identity. Whether a multi-currency Clear process also
needs a host-level instance identity remains open; it must not obscure the
currency-specific authorization boundary.

#### Internal mint and external token acceptance

The complete Clear topology must eventually support two roles:

```text
managed local Clear
    identity: local mint-service npub
    route: http://clear:3339
    scope: internal
    exposure: not published outside the Mainstay runtime

external Clear
    identity: externally managed mint-service npub when available
    route: https://clear.safebox.dev
    scope: external
    exposure: independently operated
```

Safebox Web runs inside Mainstay, so its server-side Acorn can contact the
internal route even when the browser reaches Safebox over a LAN or VPN. The
browser does not need direct access to `http://clear:3339`. An internal-only
mint therefore does not need a host port, public DNS name, or HTTPS endpoint
for Mainstay users to issue, refresh, accept, and transfer its CMUs.

The same Safebox must also be able to receive a token issued by an approved
external mint such as `https://clear.safebox.dev`. Receipt transport and mint
access are separate: the encrypted token may arrive over Spurline while proof
validation and refresh use the external Clear route.

The first implementation profile is narrower. It covers only transactions
between two Safebox/Acorn identities in one Mainstay environment using the
managed internal Clear and Spurline routes. External token acceptance is
deferred until that local path is reliable. See
[Local Clear Transactions](LOCAL-CLEAR-TRANSACTIONS-DESIGN-NOTE.md).

The target acceptance flow is:

```text
receive encrypted Clear token
    -> decode locally without contacting its advertised URL
    -> extract complete keyset ID and CMU
    -> resolve keyset ID to an approved mint-service npub
    -> verify root/service evidence and receive policy
    -> select a reachable endpoint for the current scope
    -> fetch and verify the exact public keyset
    -> refresh proofs through that selected endpoint
    -> store balance by service identity + complete keyset ID
```

The mint URL carried by a Cashu token is an advisory route. It is retained as
provenance and may seed discovery, but it must not by itself authorize a mint
or force Safebox to contact an arbitrary endpoint. This is both an identity
rule and a server-side request-forgery boundary.

The routing result differs by keyset:

```text
local keyset ID
    -> local mint-service npub
    -> internal http://clear:3339

external keyset ID
    -> external mint-service npub
    -> external https://clear.safebox.dev
```

These balances remain separate even if friendly labels match. Safebox must not
exchange, total, or substitute one CMU for the other merely because both are
implemented by Clear.

An internal-only mint also imposes an export limitation. A token advertising
only `http://clear:3339` can be accepted by Safebox instances in that Mainstay
runtime, but another Mainstay installation cannot redeem it unless it learns
an authorized route to the same mint identity through a local, external, or
FIPS binding. Mainstay should report that reachability limitation before a
user sends such a token outside the local service community.

#### Clear policy dimensions

Mainstay and Safebox should not use one URL list to represent every Clear
decision. The target configuration separates:

- **trust:** which root authorities, mint-service identities, keysets, or CMUs
  may be accepted;
- **resolution:** which verified mint-service identity is responsible for a
  complete keyset ID;
- **routing:** which internal, local, external, or FIPS endpoint reaches that
  identity from the current runtime;
- **advertisement:** which capabilities, CMUs, and routes may be disclosed to
  a particular audience; and
- **receipt policy:** whether an unknown token is rejected, quarantined for
  operator or user approval, or permitted under an explicit open policy.

The current `SAFEBOX_CLEAR_MINTS` setting is transitional. Mainstay presently
supplies both `http://clear:3339` and `https://clear.safebox.dev`; Safebox uses
the list for receive advertisement and controlled HTTP metadata lookup, while
Acorn acceptance refreshes against the mint URL carried in the token. This is
enough to exercise both routes, but it does not yet provide identity-based
resolution or a complete trust policy.

In particular, an external NIP-05 response should not publish the private
Docker hostname merely because Safebox can use it internally. Public receive
advertisement should prefer CMU or keyset identities and externally meaningful
service descriptors. Internal routes remain in the installation-scoped
registry. Local clients may receive a local projection when that disclosure is
intentional.

### Mainstay

A future Mainstay installation identity can sign its local aliases, expected
service identities, commissioning state, and endpoint policy. It is a control-
plane and deployment identity, not a super-key authorized to mint currency,
read every private message, or impersonate managed services.

## First Implementation Experiment

The first experiment should establish Clear mint-service identity and
keyset-to-service resolution without converting Cashu REST operations into
events or changing every Mainstay service.

The experiment must preserve four separate identities:

```text
currency root       -> governance continuity and service authorization
mint-service npub   -> communication, discovery, and signed responses
treasurer npub      -> authority to request permitted treasury actions
Cashu keyset ID     -> issuance keys and the corresponding CMU
```

The current Mainstay deployment has one managed local Clear instance, but the
design must not turn that process boundary into a permanent global Clear
identity. The first `CLEAR_MINT_SERVICE_NSEC` represents the initial local
currency service. A later Clear process hosting independently governed
currencies needs one service identity per currency or another explicitly
authorized identity model.

### Scope

1. Specify the canonical Clear service record that binds a currency root,
   mint-service `npub`, active and historical keyset IDs, CMUs, capabilities,
   and scoped endpoints.
2. Generate or recover a persistent managed mint-service key during Mainstay
   bootstrap, initially held as `CLEAR_MINT_SERVICE_NSEC` in `.env`.
3. Have Clear derive the `npub`, persist it as an identity sentinel beside its
   database, and refuse a missing or mismatched key over existing state.
4. Keep the new identity uncommissioned until the operator deliberately binds
   it to the Clear currency domain.
5. During root commissioning, create or install root-authorized evidence
   binding the currency's keysets and CMUs to the mint-service `npub`.
6. Add `service_identity`, management mode, and verification state to
   Mainstay's Clear registry record.
7. Resolve a complete keyset ID or `cmu-<keyset-id>` to the mint-service `npub`
   while retaining the root-authorized evidence and verification result.
8. Associate internal, local, external, and later FIPS endpoints with the
   signed service descriptor rather than with the keyset identity itself.
9. Complete a transfer between two local Acorn identities using only internal
   Clear and Spurline routes.
10. Show the mint-service `npub`, commissioning state, keyset bindings, and
    descriptor verification on the Mainstay dashboard without exposing
    private keys.

An unrooted development mint may expose a self-attested service identity, but
Mainstay must label its keyset binding as uncommissioned rather than treating
it as authoritative. No public relay publication, new Nostr event kind, FIPS
runtime, event-native mint operation, or change to Cashu REST compatibility is
required for this experiment.

This scope is a future implementation proposal only. The current Mainstay
bootstrap and service repositories do not yet create or consume these service
identity variables.

### Success criteria

- restarting or moving the managed Clear service does not change its service
  `npub`, keysets, or CMUs;
- a complete keyset ID resolves to the expected mint-service `npub` with
  inspectable authority evidence;
- internal and external endpoints can identify the same mint service without
  making either URL the identity;
- an independently operated Clear mint retains custody of its own key;
- a self-signed but uncommissioned mint is visibly distinguished from a root-
  authorized service;
- loss or replacement of `CLEAR_MINT_SERVICE_NSEC` over existing Clear state
  stops startup instead of silently creating a new identity;
- rotating the communication identity does not alter Cashu keysets,
  circulating proofs, the currency root, or `CLEAR_MASTER_SECRET`; and
- the descriptor can later add relay and FIPS bindings without changing the
  currency or keyset identity.

## Incremental Roadmap

1. **Clear identity cardinality:** settle the relationship among a Clear
   process, currency domain, mint-service identity, and multiple keysets.
2. **Clear service record:** specify canonical serialization, root authority,
   rotation, expiry, and endpoint disclosure without assigning a public event
   kind yet.
3. **Managed Clear bootstrap:** generate and verify one uncommissioned local
   mint-service identity without changing current mint or keyset behavior.
4. **Clear commissioning:** bind keysets and CMUs to the service identity with
   currency-root-authorized evidence.
5. **Mainstay resolution:** consume the managed local service record and
   resolve its keyset IDs to the verified service identity.
6. **Local Clear transfer:** prove send, relay delivery, pending receipt, and
   explicit acceptance between two local Acorns with no external fallback.
7. **External Clear import:** consume independently managed service records and
   define the trust prompt or policy for external CMUs.
8. **Spurline experiment:** apply the proven lifecycle to a relay identity and
   consume it in Mainstay and Safebox routing.
9. **Grove receipts:** sign a descriptor and one non-destructive storage or
   retrieval receipt without replacing Blossom HTTP.
10. **Transport-neutral message:** carry one harmless capability request as the
   same signed object over a relay and HTTP.
11. **FIPS adapter trial:** add a verified FIPS IPv6 endpoint to a descriptor
   while leaving the application protocol unchanged.
12. **Native FIPS trial:** after the native API stabilizes, carry the same
   protocol object by service binding and FSP port.
13. **REST projection:** move one mutating operation behind a shared capability
   handler only after replay and idempotency behavior is proven.

## Experimental Assumptions

The following assumptions need implementation evidence:

- Nostr keys are operationally suitable service identities for every listed
  service role.
- Operators can back up and rotate service keys without making local-first
  deployments too fragile.
- A compact descriptor can express enough capability and endpoint information
  without becoming a universal registry schema.
- The same signed inner protocol object can be delivered over FIPS, relays,
  and HTTP without transport-specific semantic changes.
- Event processing can preserve the exact compatibility behavior expected by
  existing Cashu and Blossom clients.
- Endpoint scope policy can remain local even when descriptors are exchanged
  externally.
- The evidentiary value of signed responses justifies their lifecycle and
  storage cost for selected consequential operations.

## Open Questions

1. Which entity commissions a Mainstay installation identity, and is one
   required for a standalone service?
2. What exact event kind and `d` value should identify service descriptors?
3. Should descriptor expiry fail closed during prolonged offline operation, or
   may a locally pinned last-known-good descriptor remain usable?
4. What authority signs `keyset_id -> mint service npub` for conventional
   Cashu mints that have no Clear currency root?
5. Can public aliases be useful without recreating DNS governance and naming
   disputes?
6. What naming authority owns capability names, and how are incompatible
   versions retired?
7. Should request and response event kinds be capability-specific or use a
   constrained generic envelope?
8. How long must idempotency and replay records survive for each consequential
   capability?
9. Which progress and error events deserve durable storage?
10. Does a service sign plaintext before encryption, sign ciphertext, or use a
    signed inner event plus encrypted transport envelope?
11. Can one inner object be used unchanged by FIPS, NIP-59 relay delivery, and
    HTTP without leaking transport-specific metadata?
12. When may a service identity equal its FIPS node identity, and who holds the
    shared secret?
13. How does a host-level FIPS node prove bindings for several service npubs
    and ports?
14. How do REST authentication methods map to event authorization without
    falsely attributing a gateway signature to the client?
15. Does a multi-currency Clear process need an instance identity in addition
    to each currency's mint-service identity?
16. Should service descriptors be published, privately replicated, carried on
    demand, or distributed by the Mainstay installation?
17. Which signed records are evidence, which are operational logs, and which
    must be deliberately discarded for privacy?
18. What explicit commands and evidence move a service between `managed`,
    `external`, and `compatibility` modes?

## Ownership Boundaries

Mainstay owns:

- bootstrap, custody, rotation, and commissioning for managed identities;
- verification and pinning, but not private-key custody, for external
  identities;
- identifier resolution policy and verified caches;
- descriptor verification and capability selection;
- endpoint scope policy and transport choice; and
- orchestration across Docker, jails, and future runtimes.

Each application service owns:

- its protocol semantics and authorization rules;
- its service key custody or signing boundary;
- validation, idempotency, and consequential state transitions; and
- signed results and domain-specific evidence.

FIPS owns:

- npub-based node reachability;
- mesh routing and peer discovery;
- link and session transport security;
- IPv6 adaptation and `.fips` address preparation; and
- the native datagram interface when stabilized.

Nostr specifications own the common event and signature format and any adopted
encryption or relay-delivery profiles. Spurline and other relays transport and
store events according to policy; they do not become the authority for the
application claims inside those events.

## Desired End State

```text
keyset ID
    -> resolve with evidence
mint service npub
    -> discover signed descriptor
mint capabilities
    -> construct signed protocol object
available scoped transports
    -> select FIPS, relay, or HTTP
mint service
    -> return signed response
verified evidence
```

The same sequence applies to Grove, Spruce, Safebox Web, Spurline, and future
Mainstay services. They should increasingly interact by knowing identities and
capabilities rather than by treating hard-coded URLs as identity.

> Resolve the identity. Discover the capability. Send the message. Choose the
> transport. Verify the evidence.

## References

- [Address Spaces, Endpoint Scopes, and FIPS](ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md)
- [Local-First Hypervisor and FIPS](LOCAL-FIRST-HYPERVISOR-AND-FIPS-DESIGN-NOTE.md)
- [FIPS design overview](https://github.com/jmcorgan/fips/blob/master/docs/design/README.md)
- [FIPS architecture](https://github.com/jmcorgan/fips/blob/master/docs/design/fips-architecture.md)
- [FIPS IPv6 adapter](https://github.com/jmcorgan/fips/blob/master/docs/design/fips-ipv6-adapter.md)
- [FIPS native API](https://github.com/jmcorgan/fips/blob/master/docs/design/fips-native-api.md)
- [NIP-01 event format and kind ranges](https://github.com/nostr-protocol/nips/blob/master/01.md)
- [NIP-44 encrypted payloads](https://github.com/nostr-protocol/nips/blob/master/44.md)
- [NIP-59 gift wrapping](https://github.com/nostr-protocol/nips/blob/master/59.md)
- [Clear multi-currency authority model](https://github.com/trbouma/clear/blob/main/docs/MULTI-CURRENCY-TREASURER-AUTHORIZATION-DESIGN.md)
