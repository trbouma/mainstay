# Ecosystem Responsibility Boundaries and Iterative Development

## Status

This note records an engineering method learned while integrating the Mainstay
product family. It complements the Mainstay house style and identity-resolution
notes by defining how requirements should be assigned across repositories and
how those assignments support rapid, safe iteration.

## Conclusion

> Give each meaning one authoritative owner, then pass only the evidence and
> context required by the next layer.

Mainstay is useful partly because it makes relationships among independently
useful services visible. When a requirement crosses several products, the goal
is not to move all logic into Mainstay. The goal is to identify which component
owns the invariant meaning, which component knows the current operating
context, which component performs the portable protocol operation, and which
component explains the result to the user.

Clear responsibility boundaries make ecosystem requirements easier to reason
about. They also shorten the development cycle: each repository receives a
small, testable change instead of sharing one ambiguous implementation across
several layers.

## Responsibility Map

| Component | Authoritative responsibility | Context it consumes | What it must not silently own |
| --- | --- | --- | --- |
| Clear | CMU identity, mint operations, proof state, supply accounting, treasury authorization, and transfer semantics | Authorized keysets, treasury policy, service identity, and mint requests | Wallet acceptance, recipient relay choice, or deployment topology |
| Acorn | Portable wallet authority, keys, proofs, records, resolution, protocol execution, and send guards | Stable identifiers, recipient capabilities, and candidate service routes | Product presentation, infrastructure lifecycle, or issuer policy |
| Safebox Web | User workflows, explanation, confirmation, and application-level error handling | Acorn results, verified metadata, and Mainstay-provided defaults | Mint accounting, relay semantics, or claims unsupported by evidence |
| Mainstay | Deployment lifecycle, local service context, scoped endpoints, installation identity, and coordination policy | Service health, identities, operator configuration, and external relationships | User key custody, mint authority, protocol reimplementation, or universal trust decisions |
| Spurline | Nostr event acceptance, storage, query, and relay delivery | Standard events, relay policy, and service configuration | Application meaning, mint validity, or recipient acceptance |
| Grove | Opaque content-addressed blob storage and retrieval | Ciphertext, content digests, authorization, and service configuration | Plaintext meaning, record policy, or application ownership |
| Stroma | Nostr wire format, signing, encryption, gift wrapping, and bounded relay exchange | Keys, events, and relay calls supplied by its caller | Wallet policy, service operation, or user experience |
| FIPS or another transport | Identity-aware network reachability | Destination identity, routing policy, and protocol traffic | Application semantics, service authority, or acceptance policy |

These are ownership boundaries, not communication barriers. A component may
report evidence used by another without becoming authoritative for the decision
made at that other layer.

## Worked Example: Clear Availability

The `Private / Local / Across networks` terminology shows the method clearly.

The user asks a simple question:

> Can I transfer this Clear balance to that person?

The answer contains several independent questions:

1. Which exact CMU and proofs are being transferred?
2. Which mint service is responsible for that keyset?
3. Can the recipient receive the encrypted token?
4. Can the recipient reach that mint to verify and refresh the proofs?
5. Does the recipient recognize and accept the CMU?
6. Which treasurer stands behind its issuance and liability?

No single component can answer all six honestly.

### Clear owns the meaning

Clear defines CMU identity, proof validity, treasury authority, and what it
means for a Mint Note to be transferable by protocol. It can advertise its
service identity and supported capabilities. It does not know whether two
wallets share one Mainstay context or whether a recipient wants the CMU.

### Mainstay supplies local context

Mainstay knows which Clear and Spurline services belong to its installation and
which internal routes are eligible for co-resident callers. It may also supply
local routes shared with other participating instances and configured
cross-network route candidates. It does not decide that a CMU is trusted or
accepted merely because its mint is available.

### Acorn resolves and guards

Acorn combines stable CMU, service, and recipient identities with the current
context. It resolves mint and inbox routes and stops an unsafe transfer before
proof export when the recipient cannot use an internal-only mint.

### Safebox Web explains and confirms

Safebox Web presents the derived availability as `Private`, `Local`, or `Across
networks`, shows treasury and recognition information separately, and asks for
the user's decision. It does not infer trust from reachability.

### Spurline delivers without interpreting

Spurline carries the encrypted Nostr transfer. Successful relay publication
does not mean the proofs are valid, the mint is reachable, or the recipient has
accepted the CMU.

This division produces one coherent experience without assigning contradictory
authority to any component.

## Requirements Within One Ecosystem

Inside the Mainstay family, shared conventions allow a direct integration:

```text
service reports stable identity and capability
    -> Mainstay supplies scoped deployment context
    -> Acorn resolves and performs the protocol operation
    -> Safebox Web presents the result
```

Repositories may evolve together, but each remains independently testable and
deployable. Shared development does not justify bypassing public service
boundaries, reading another service's database, or duplicating its policy.

The preferred integration artifact is the smallest stable contract that
crosses the boundary:

- a service information response;
- a signed Nostr record;
- a stable identifier and capability descriptor;
- a narrow library API;
- a scoped environment value; or
- an explicit command result.

## Requirements Across Ecosystems

An independent Clear mint, Blossom server, relay, wallet, or future Mainstay
installation cannot rely on Mainstay's internal configuration. Cross-ecosystem
operation therefore begins with portable facts:

- stable cryptographic or content identities;
- explicit protocol capabilities;
- independently resolvable routes;
- signed authority or commissioning evidence where required;
- clear version and compatibility rules; and
- honest unknown states when evidence is unavailable.

Mainstay may provide an initial hint, but the portable component must be able to
resolve or refresh that relationship without permanent dependence on the
originating installation. Compatibility modes may retain URL-based behavior,
but must not present location as cryptographic identity.

This approach makes an ecosystem edge visible. When an operation works inside
one Mainstay instance but fails across instances, the missing requirement can
be named precisely: external delivery, mint reachability, capability discovery,
identity binding, authority evidence, or recipient acceptance. That is far more
actionable than treating the failure as generic networking.

## The Iterative Development Cycle

Cross-repository work should follow a compact sequence.

### 1. Start with the user question

Express the practical decision the user or operator needs to make. Avoid
starting with an environment variable, endpoint, or database field.

### 2. Separate independent dimensions

List the facts hidden inside the question. Reachability, identity, authority,
acceptance, health, and finality often vary independently and should not be
collapsed into one status.

### 3. Assign one authoritative owner per meaning

Choose the component that can establish each fact without guessing. Other
components may cache, present, or act on the fact, but should preserve its
provenance and uncertainty.

### 4. Define the smallest cross-boundary contract

Add only the identifier, evidence, capability, or result needed by the next
layer. Prefer established APIs, signed records, and protocol structures over
database coupling or duplicated parsing.

### 5. Preserve standalone behavior

Mainstay-provided defaults and context must remain optional inputs. Clear,
Grove, Spurline, Safebox Web, and Acorn should retain coherent independent
operation unless a requirement explicitly defines a managed-only profile.

### 6. Implement from authority toward presentation

Establish semantics and producer behavior first, then portable resolution and
guards, then deployment context, and finally user presentation. Temporary
compatibility behavior should be labeled as such.

### 7. Test the matrix, not only the happy path

Test meaningful combinations across boundaries. For Clear availability these
include private, local, and cross-network mint routes, same and different
Mainstay contexts, available and unavailable relays, recognized and unknown
treasurers, and pending versus confirmed proofs.

### 8. Record the result where each audience needs it

The protocol repository records the invariant. Mainstay records deployment and
integration behavior. The user-facing application explains the decision in
plain language. Cross-links preserve one coherent account without copying the
same authority into every repository.

## Why This Tightens the Development Cycle

Explicit ownership reduces several common sources of delay:

- requirements stop bouncing among repositories because their semantic owner
  is named;
- tests can be written at the smallest responsible boundary;
- integration failures reveal a missing fact or contract instead of an
  undifferentiated application bug;
- standalone services can be validated before Mainstay integration;
- compatibility paths remain available while identity-based paths mature;
- one component can evolve internally without forcing unrelated consumers to
  change; and
- documentation can distinguish implemented behavior, provisional heuristics,
  and future architecture.

The result is not fewer components. It is less ambiguity between them.

## Review Questions

For any new cross-product requirement, ask:

1. What user or operator decision are we supporting?
2. Which facts in that decision can vary independently?
3. Which component is authoritative for each fact?
4. What stable identifier crosses the boundary?
5. What current context or route is required?
6. What evidence justifies the result, and what remains unknown?
7. Does the change preserve standalone operation?
8. How does failure appear before irreversible state or value moves?
9. Which unit, contract, integration, and field tests cover the matrix?
10. Which repository explains the invariant, integration, and user language?

## Related Notes

- [Mainstay House Style and Family Audit](MAINSTAY-HOUSE-STYLE.md)
- [Invariant Identity and Dynamic Resolution](INVARIANT-IDENTITY-AND-DYNAMIC-RESOLUTION.md)
- [Identity, Resolution, and Event-Native Services](IDENTITY-RESOLUTION-AND-EVENT-NATIVE-SERVICES.md)
- [Clear Availability, Acceptance, and Authority](CLEAR-TRANSFER-SCOPE-ACCEPTANCE-AND-AUTHORITY.md)
- [Clear CMU Transferability, Acceptance, and Authority](https://github.com/trbouma/clear/blob/main/docs/CMU-TRANSFERABILITY-ACCEPTANCE-AND-AUTHORITY.md)
