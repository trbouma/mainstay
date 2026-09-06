# Clerk and Treasury Functions

## Status

This is an architectural design note. It introduces a conceptual frame for
Mainstay without creating applications, services, user roles, event kinds, or
implementation requirements named Clerk or Treasury.

The frame is intended to simplify how Mainstay describes its purpose:

> Mainstay provides infrastructure for Clerk and Treasury functions:
> preserving verifiable evidence of consequential acts and accountable,
> transferable claims without requiring the applications that created them to
> remain the ultimate source of truth.

This statement does not make Mainstay an institutional authority, system of
record, mint, or source of legal effect. Institutions define authority and
recognition. Protocols make evidence and instruments portable and verifiable.
Services keep the necessary data and operations available.

## Terminology

### Functions, not products

The **Clerk function** and **Treasury function** are enduring institutional
capabilities. They are not proposed application names, containers, or
exclusive user roles.

The word **treasurer** remains available for a person, governance role, or key
authorized to perform specific treasury operations. This is especially
important in Clear, where treasurer identities are distinct from the currency
root, mint-service identity, and Cashu keysets. The architectural function is
therefore called **Treasury**, not **Treasurer**.

The same separation applies if Mainstay later introduces a clerk actor or
service identity. An actor may exercise part of the Clerk function without
becoming the function itself.

### Three Mainstay layers

The name Mainstay currently spans related but distinct layers:

| Layer | Meaning |
| --- | --- |
| Mainstay product | The user-facing application and coherent experience |
| `mainstay-local` and Lockbox | The deployment control plane and integrated appliance |
| Mainstay family | The independently useful protocols and services coordinated by the product |

The Clerk and Treasury functions span these layers. They do not replace the
product model:

```text
Mainstay is the application.
Lockbox is the appliance.
The Mainstay family supplies the protocols and services.
Clerk and Treasury describe the institutional functions they support.
```

## The Clerk Function

The Clerk function concerns records, evidence, validation, control, and
consequence. It helps a relying party answer:

> What verifiable evidence exists, and what state follows from it under an
> identified set of rules?

This is more precise than claiming that software determines what happened.
A signature can establish who signed an event and what the event says. It does
not by itself prove every real-world assertion in that event. Validation can
derive protocol state under identified rules. It does not by itself compel an
institution or relying party to recognize that state or give it legal effect.

The Clerk function should support:

- identifying exact digital objects;
- preserving authorized statements and acts as signed evidence;
- binding evidence to actor and service identities;
- maintaining verifiable and replayable history;
- identifying the rules and rule versions used for validation;
- establishing and transferring protocol-defined control;
- applying standing, recognition, and other effect rules without conflating
  them;
- deriving consequential state from valid evidence;
- preserving revocation, succession, and continuity evidence; and
- presenting evidence independently of the application that created it.

The conceptual sequence is:

```text
Digital Object
    -> Evidence
    -> Validation under identified rules
    -> Consequential State
    -> Recognition or effect by a relying party
```

OpenETR provides much of the intended grammar. Mainstay should preserve its
separation between:

```text
Digital Object -> Digital Original
```

and its parallel primitive families:

| Effect primitives | Control primitives and transitions |
| --- | --- |
| Recognition | Issue / Create |
| Standing | Transfer |
| Relinquishment | Encumber |
| | Discharge |
| | Release |
| | Terminate |

Encumbrance and discharge establish and remove guards on permissible control
transitions. Mainstay applications should consume these concepts rather than
inventing application-specific substitutes.

## The Treasury Function

The Treasury function concerns units of value, claims, obligations, issuance,
transfer, redemption, and settlement. It helps a participant answer:

> What instruments are held, what obligations do they represent, and what is
> currently transferable or redeemable?

The answer may depend on more than possession. A bearer note can carry a valid
issuer signature while already having been spent. For Cashu, the issuing mint
normally remains necessary to establish current spendability and to redeem or
refresh a note. Offline possession and signature verification must not be
presented as proof of current settlement.

The Treasury function should support:

- defining bounded units and their governing authority;
- establishing a treasury and its operating policies;
- commissioning mints and authorized treasury actors;
- issuing notes or claims;
- holding and accounting for reserves or backing assets where applicable;
- preserving liabilities independently from a wallet presentation;
- holding and transferring bearer instruments;
- validating current spendability through the responsible service;
- redeeming, settling, and retiring obligations;
- rotating services and keys without silently changing an instrument's
  identity; and
- producing evidence suitable for reconciliation and audit.

A generic lifecycle is:

```text
Establish Treasury
    -> Commission authority and services
    -> Define unit
    -> Issue
    -> Hold
    -> Transfer
    -> Redeem or settle
    -> Retire
```

The following concepts must remain distinct:

| Concept | Meaning |
| --- | --- |
| Treasury | The institutional function and governed obligations |
| Treasurer | An actor or key authorized for defined treasury operations |
| Mint | A service that issues, validates, refreshes, and redeems instruments |
| Note | A transferable bearer instrument |
| Mint unit | A denomination or accounting unit |
| Keyset | Issuance keys that identify and validate a class of notes |
| Settlement or reserve layer | The mechanism supporting or satisfying the obligation |

Cashu is the current bearer-note mechanism used by Safebox and Clear. It is not
the definition of a treasury. Clear may support treasury models with different
reserve or settlement arrangements while retaining Cashu-compatible notes at
the wallet boundary.

## Functional Symmetry

The two functions address a shared continuity problem: something important
must remain interpretable beyond the interaction and application that created
it.

| Clerk function | Treasury function |
| --- | --- |
| Records and consequential acts | Value, claims, and obligations |
| Signed evidence | Instruments and accounts |
| Validates under rules | Validates under issuance and settlement policy |
| Maintains verifiable history | Maintains liabilities and settlement history |
| Derives consequential state | Determines instrument state under issuance and settlement rules |
| Supports recognition and effect | Supports transfer and redemption |
| What evidence exists and what follows? | What is held, owed, transferable, or redeemable? |

The symmetry is useful, but it is not equivalence. A record and a bearer note
have different replay, privacy, finality, and double-spend properties. Shared
infrastructure must not erase those domain-specific invariants.

## Shared Mainstay Substrate

The functions should share infrastructure where the security and authority
boundaries genuinely align.

```text
                         MAINSTAY

              CLERK                  TREASURY
        records and evidence       claims and value
                 |                       |
             validation              instrument state
                 |                       |
        consequential state      transfer and redemption
                  \                     /
                   \                   /
                    SHARED SUBSTRATE
               identity | resolution
                events | discovery
               content | transport
             custody | local operation
```

### Identity

Every independently addressable Mainstay service should have a stable
cryptographic identity when it signs responses, receives private messages,
advertises capabilities, or must be distinguished from another service
instance.

A service descriptor may advertise:

- service identity and type;
- capabilities and protocol versions;
- scoped endpoints and transport options;
- relevant domain keys and identifiers;
- operator, installation, and peer relationships; and
- continuity or successor evidence.

Service identity remains distinct from operator identity, installation
identity, Cashu keysets, Acorn identities, object digests, and network
locations.

### Resolution and discovery

Resolution identifies the service identity responsible for a stable
identifier:

```text
identifier -> responsible service npub
```

Discovery then describes what that service can do and how it can be reached.
For example:

```text
Cashu keyset ID
    -> authorized mint-service identity
    -> capability descriptor
    -> internal, local, external, or FIPS route
```

The resolver supplies verified routing and authority evidence. It does not
become the authority over the underlying record, currency, or instrument.

### Events

Signed events can provide a common substrate for identity, authorization,
discovery, requests, approvals, receipts, audit evidence, revocation, and
succession. They do not make every operation event-native.

Mainstay must distinguish:

- ephemeral communication;
- operational records needed for safe processing; and
- consequential evidence whose verification changes rights or obligations.

A Nostr event acknowledging a mint operation is evidence about the operation.
It is not a substitute for Cashu double-spend state, proof validation, mint
accounting, or settlement. Existing Cashu NUT endpoints remain authoritative
for compatibility clients until a separately specified event-native profile
exists.

### Content

Large immutable content can remain digest-addressed and stored through Grove
or another Blossom-compatible service. Signed evidence can bind to exact bytes
without requiring the event transport to carry the complete object.

Content availability and evidentiary meaning remain separate. A Grove server
can prove that it serves bytes matching a digest without deciding what those
bytes mean or whether a relying party recognizes them.

### Transport and local operation

HTTP, WebSocket, Nostr relays, FIPS, Docker names, LAN addresses, and FreeBSD
jail addresses are transports or locator forms. They must not become durable
identity.

`mainstay-local` and Lockbox supply the operational substrate: service startup,
health, endpoint selection, backup, recovery, key injection, migration, and
default-deny exposure. These capabilities are first-class Mainstay work even
though they do not belong exclusively to either institutional function.

## Component Map

Components need not fit exclusively into one column.

| Component | Clerk function | Treasury function | Shared substrate |
| --- | --- | --- | --- |
| Mainstay product | Presents records, evidence, and derived state | Presents balances, instruments, and settlement state | Provides one coherent user experience |
| `mainstay-local` | Operates required local services | Operates required local services | Orchestration, identity injection, endpoints, health, backup |
| Lockbox | Durable local record availability | Durable local wallet and mint availability | Appliance, storage, supervision, hardware controls |
| Safebox Web | Record and evidence workflows | Wallet, transfer, acceptance, and payment workflows | Browser compatibility and presentation |
| Safebox Acorn | User keys, signing, records, and control operations | Proof custody, mint resolution, transfer, and recovery | Portable user authority |
| OpenETR | Object identity, evidence grammar, validation, and consequential state | May provide evidence about treasury authority or obligations | End-verifiable state derivation patterns |
| Clear | Root policy and signed treasury evidence | Units, issuance, minting, redemption, and liabilities | Service identity and resolution records |
| Stroma | Signed and encrypted evidence encoding | Signed treasury messages where specified | Narrow Nostr wire boundary |
| Spurline | Durable event distribution and replay | Treasury messages and receipts where specified | Local relay and future synchronization |
| Grove | Digest-addressed records and attachments | Reserve or settlement artifacts where appropriate | Opaque content-addressed storage |

This table describes architectural participation, not ownership. Each
component retains the authority and failure boundaries defined by its own
protocol and repository.

## Authority Boundaries

The Clerk and Treasury frame must preserve these invariants:

1. Mainstay presents and coordinates state; it does not become the authority
   merely because it presents the result.
2. A signature proves control of a key and integrity of signed content, not
   every real-world assertion in that content.
3. Validation derives state under named rules; recognition and legal effect
   remain with the responsible institution or relying party.
4. Possession of a bearer note does not by itself establish that the note is
   currently unspent.
5. A mint-service identity is distinct from a currency root, treasurer,
   keyset, unit, and endpoint.
6. A relay retains and distributes signed events without becoming their
   author or authority.
7. A storage service preserves digest-addressed bytes without interpreting
   their institutional meaning.
8. A compatibility gateway must not attribute its own signature to an
   unsigned client request.
9. Protocol portability does not guarantee service availability. Mainstay
   must describe what remains verifiable, transferable, or redeemable when a
   dependency is unavailable.

## Design Tests

New functionality should be evaluated with three questions.

### Clerk test

Does this capability help preserve or interpret verifiable evidence of an act,
including what state follows under identified rules?

### Treasury test

Does this capability help define, hold, account for, transfer, redeem, or
settle a governed claim or obligation?

### Substrate test

Does this capability sustain the trustworthy identity, custody, availability,
resolution, or operation required by either function?

If the answer to all three is no, the capability may be an application
convenience rather than part of the Mainstay architecture. Application
conveniences can still be valuable, but they should not silently redefine the
protocol or authority model.

## Capability Gaps

The frame exposes work that is not complete merely because the current
applications can demonstrate a workflow.

### Clerk gaps

- canonical identifiers and versioning for validation rule sets;
- portable verifier outputs that include evidence provenance;
- explicit evidence completeness and uncertainty reporting;
- revocation, succession, and conflicting-evidence handling;
- ordering and time semantics that do not depend on one database clock; and
- durable presentation bundles that can be verified independently.

### Treasury gaps

- an explicit treasury identity and governance model;
- a liability and issuance account distinct from wallet proof state;
- commissioning evidence for roots, treasurers, mints, units, and keysets;
- reserve or backing attestations where the treasury model requires them;
- pluggable reserve and settlement layers;
- redemption, retirement, and exceptional recovery policy;
- keyset and mint-service succession without changing instrument identity; and
- audit and reconciliation outputs that do not expose bearer secrets.

### Shared gaps

- installation and service identity bootstrap for every managed service;
- signed relationship and successor records;
- resolver provenance, expiry, and conflict rules;
- audience-aware capability and endpoint advertisement;
- backup and recovery procedures for identities and component data; and
- FIPS transport integration without changing protocol semantics.

These are design and implementation questions, not commitments to one
monolithic framework.

## Implementation Direction

Introducing this frame does not justify a broad refactor. Near-term work should
continue through existing component boundaries.

1. Use the Clerk, Treasury, and substrate tests when reviewing new features.
2. Reuse the existing service identity and endpoint resolution model.
3. Keep OpenETR terminology authoritative for Clerk-oriented control and
   effect primitives.
4. Develop Treasury vocabulary in Clear without making Mainstay synonymous
   with Cashu.
5. Preserve REST and existing protocol interfaces while producing durable
   evidence where it has defined meaning.
6. Document authority, current availability, and failure behavior before
   introducing cross-service automation.
7. Recommend significant code restructuring separately from documentation
   changes.

The first implementation milestones remain concrete workflows, such as local
Clear transfer and independently verifiable record presentation. The new frame
helps judge those workflows; it does not replace their protocol-specific
design notes.

## Relationship to Existing Notes

This note supplies the institutional frame above the existing technical
designs:

- [Mainstay Identity, Resolution, and Event-Native Services](IDENTITY-RESOLUTION-AND-EVENT-NATIVE-SERVICES.md)
  defines service identities, resolution, capabilities, evidence, and
  transport-independent messaging.
- [Address Spaces, Endpoint Scopes, and FIPS](ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md)
  separates durable identity from internal, local, external, and FIPS routes.
- [Local-First Hypervisor and FIPS](LOCAL-FIRST-HYPERVISOR-AND-FIPS-DESIGN-NOTE.md)
  defines the `mainstay-local` control plane and migration path from Docker to
  FreeBSD jails.
- [Local Clear Transactions](LOCAL-CLEAR-TRANSACTIONS-DESIGN-NOTE.md)
  defines the first bounded Treasury workflow inside one Mainstay environment.

OpenETR remains the source for its own object, evidence, control, effect, and
validation terminology. Clear and Cashu remain the sources for mint, proof,
unit, issuance, and redemption semantics.

## Open Questions

- What evidence identifies and governs a treasury independently of a mint
  process?
- Which treasury facts should be public, selectively disclosed, or private?
- Which OpenETR verifier outputs should Mainstay cache, and what provenance
  must accompany that cache?
- When should a consequential HTTP operation produce a signed receipt without
  turning the operation itself into an event-native protocol?
- Which service relationships are attested by an operator, a Mainstay
  installation, a currency root, or another governance authority?
- How should Mainstay express degraded operation when evidence remains
  verifiable but content, mint validation, redemption, or settlement is
  temporarily unavailable?
- Can a common audit envelope serve both functions without conflating record
  consequence with monetary finality?
