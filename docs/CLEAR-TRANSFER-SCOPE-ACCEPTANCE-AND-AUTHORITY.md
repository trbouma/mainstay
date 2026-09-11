# Clear Availability, Acceptance, and Authority

## Status

This note defines user-facing terminology and architectural distinctions for
presenting Clear Mint Units in Safebox Web under Mainstay. It builds on the
implemented local-transfer guard and current external HTTPS mint heuristic. It
does not define a universal acceptance system, certify any CMU, or complete the
future multi-route mint resolver.

## Summary

Safebox Web should describe the practical availability of a Clear balance with
three user-facing values:

- **Private**
- **Local**
- **Across networks**

Availability answers where a token can be sent with a usable route back to
its mint. It does not answer whether the recipient recognizes the CMU, trusts
its treasurer, values it at par, or is willing to accept it.

The governing rule is:

> Transferability, acceptance, and authority are separate dimensions.

Keeping them separate lets a wallet explain Clear balances plainly without
turning network reachability into an endorsement.

## Why Availability Is Useful

A bearer token can be delivered to a recipient even when that recipient cannot
reach its mint. Delivery alone is therefore not a useful definition of a
successful Clear transfer. The recipient must also be able to verify and
refresh the proofs through a route associated with the correct mint and
keyset.

Mainstay distinguishes three practical cases for a wallet user.

### Private

The token can be transferred among authorized members whose wallets share one
Mainstay instance and its internal Clear and Spurline services.

```text
Availability: Private
```

Supporting copy:

> Usable by members of this Mainstay instance.

All Clear bearer transfers are cryptographically private. This label adds a
different fact: the usable service boundary is private to one instance and its
members.

### Local

The token can be transferred between participating Mainstay instances using
shared local infrastructure. The Clear mint and recipient delivery route are
available on that infrastructure without requiring internet access.

```text
Availability: Local
```

Supporting copy:

> Usable between participating instances on this local network.

Local describes a deliberately shared operating boundary, not a single
process or a claim of geographic closeness. Each instance retains its own
governance, identities, data, and acceptance policy.

### Across networks

The mint advertises a route intended to be reachable outside the sender's
local network boundary, and the recipient has a suitable delivery path.

```text
Availability: Across networks
```

Supporting copy:

> The mint can be reached outside this local system. The receiving wallet still
> decides whether to accept the CMU.

Today, a LAN-address or local-DNS mint URL is the provisional signal for
**Local**, and an eligible external HTTPS mint URL is the provisional signal
for **Across networks**. The future resolver should derive either state from
verified endpoint scope, federation, or FIPS routes without making an FQDN
part of the CMU's identity.

"Across networks" is intentionally different from "global." It does not promise
universal Internet availability, unrestricted access, or acceptance everywhere.
It says that transfer is not confined to one shared local network. The route
may still be private, authenticated, and limited to participating communities.

## Independent Dimensions

### 1. CMU identity

The complete Clear keyset ID identifies the issuance keyset represented by the
proofs. The canonical `cmu-<keyset-id>` keeps balances from different keysets
separate even when they use the same friendly name or mint service.

CMU identity answers:

> Which exact issuance instrument is this?

It does not identify the current mint URL, determine availability, or imply
recognition.

### 2. Availability

Availability is a derived operational statement about the routes currently
available to a sender and intended recipient.

It answers:
> Can the recipient receive the token and reach the responsible mint from its
> service context?

The state is not permanently embedded in the token. A mint may gain, lose, or
replace an external route while retaining the same service identity and
keysets. Safebox should resolve availability as late as practical and may
change the display when verified reachability changes.

### 3. Acceptance and recognition

Acceptance is the recipient's decision to receive and retain a particular CMU.
Recognition is the policy or prior relationship that helps inform that
decision. Either may be personal, organizational, or community-specific.

Acceptance answers:

> Am I willing to receive this CMU under the terms and relationships I
> understand?

A CMU can be technically transferable across networks and still be unknown or
unacceptable to the recipient. Conversely, a community may recognize a local
CMU even though it is intentionally transferable only through its local
Mainstay services.

Safebox must not infer acceptance from any of the following:

- presence on the same Mainstay instance;
- successful mint or relay reachability;
- an external HTTPS mint address;
- possession of valid ecash proofs;
- commissioning of the mint service; or
- recognition by another wallet, venue, or organization.

### 4. Treasury authority

The treasurer is the authority responsible for issuance and liability under the
rules of a particular Clear currency. Treasury authority is distinct from the
Mainstay operator, Clear service operator, mint service identity, and network
route.

Authority answers:

> Who stands behind this CMU, and under what policy is it issued and redeemed?

Several treasurers may operate currencies reachable through one Mainstay
environment. Co-location provides connectivity, not common governance. A
Mainstay operator commissioning a Clear service attests to the service's place
in that installation; it does not silently endorse every CMU or assume every
treasury liability.

### 5. Service identity and reachability

The Clear service `npub` identifies the mint service independently of its
addresses. Internal HTTP, public HTTPS, and future FIPS locators are routes to
that service.

Service identity and endpoint verification answer:

> Is this route serving the mint service expected for this keyset?

Reachability is evidence used to derive availability. It is not evidence that
the CMU is valuable, well governed, solvent, or accepted.

### 6. Delivery path

The recipient's inbox relay carries the encrypted transfer. The relay path is
independent of the mint path: a token may reach the recipient through an
external relay while naming an internal-only mint that the recipient cannot
use.

Delivery answers:

> Can the encrypted token reach this recipient identity?

A safe transfer requires both a suitable delivery path and suitable mint
reachability.

### 7. Operational state and finality

An eligible route may be advertised while temporarily unavailable. Proofs may
also be pending verification or refresh. Current health and proof state should
therefore remain separate from the more durable availability classification.

Operational state answers:

> Is the required service reachable now, and has this wallet finalized the
> received value?

## Decision Matrix

| Availability | Acceptance | Treasury recognition | User meaning |
| --- | --- | --- | --- |
| Private | Accepted | Recognized | Usable by participating members of this instance |
| Private | Not established | Unknown or unrecognized | Instance services are usable, but no acceptance should be implied |
| Local | Accepted | Recognized | Usable between participating instances on local infrastructure |
| Local | Not established | Unknown or unrecognized | A local route exists, but no acceptance should be implied |
| Across networks | Accepted | Recognized | Recipient accepts the CMU and can reach its mint outside the sender's context |
| Across networks | Not established | Unknown or unrecognized | Technically portable, but not necessarily wanted or trusted |

The matrix deliberately permits every combination. Availability must not be
used as a proxy for acceptance, and local connectivity must not be used as a
proxy for treasury recognition.

## Safebox Web Presentation

Safebox should use a compact primary label with progressively disclosed detail.
For example:

```text
Clear Credits                         120 credits
Availability: Private
Treasurer: North Shore Cooperative
Recognition: Recognized by this community
```

```text
Market Credits                        75 credits
Availability: Local
Treasurer: Regional Cooperative
Recognition: Recognized by this community
```

```text
Community Credits                     40 credits
Availability: Across networks
Treasurer: External issuer
Recognition: Not yet established
```

The first implementation does not need to invent recognition data that does
not exist. It may show only verified fields and use an honest unknown state:

```text
Availability: Across networks
Treasurer: Not verified
Recognition: Not established
```

The send confirmation should explain the practical boundary:

- for **Private**, the recipient must be a member using the same instance;
- for **Local**, the recipient's instance and mint must share eligible local
  routes;
- for **Across networks**, the mint advertises a route outside the local
  context, but the receiver still chooses whether to accept the CMU; and
- when availability cannot be established, Safebox must stop before exporting
  proofs or require a deliberate expert override with a precise warning.

## Terminology Decisions

The labels describe availability boundaries rather than acceptance:

| Rejected wording | Reason |
| --- | --- |
| `Local / Global` | Global suggests universal reach and acceptance |
| `Locally accepted / Widely accepted` | Acceptance cannot be inferred from network paths |
| `Private / Public` | Public overstates exposure and acceptance; Private is retained only for the instance membership boundary |
| `Trusted / Untrusted` | Reachability does not establish treasury trust |
| `Venue only / Beyond venue` | Useful for some brands, but too specific as a universal product term |
| `Non-local transferable` | Technically suggestive but awkward for users |

`Private / Local / Across networks` distinguishes one house, cooperation among
nearby houses, and cooperation across network boundaries. It remains neutral
across communities, Indigenous Nations, cooperatives, organizations, resorts,
campuses, and independent deployments. Experience profiles may adapt
explanatory nouns to language chosen by the operator or community, but they
must not change the underlying meaning.

## A Limited Historical Parallel

The model has a modest historical parallel in the Florentine florin. The gold
florin was issued by the Republic of Florence beginning in the thirteenth
century, yet became recognized and trusted as trading currency well beyond
Florence. Its circulation and acceptance extended beyond the jurisdiction of
its issuer rather than being produced by one uniform, continent-wide monetary
authority.

The analogy should not be pushed too far. Florence itself was a public issuing
authority, medieval money was regulated, and the material properties and
verification model of a gold coin differ fundamentally from ecash. The useful
lesson is narrower: **issuance authority, geographic or network circulation,
and voluntary acceptance are related but distinct.** A currency may originate
under one bounded authority and become useful elsewhere because other people
independently recognize it.

The British Museum notes that the florin and Venetian ducat were recognized and
trusted as trading currencies throughout Europe after their introduction in
the 1200s, with long-lived designs contributing to that trust. See the
[British Museum Money Gallery guide](https://www.britishmuseum.org/sites/default/files/2021-05/Money_Gallery_LPG_2020_Room_68.pdf).

Clear makes these distinctions explicit in software rather than assuming that
reach, authority, and acceptance collapse into one national currency boundary.

## Implementation Direction

1. Add `Private`, `Local`, and `Across networks` as derived Safebox display
   states, not new CMU identifiers or token fields.
2. Base the first version on internal, private-address or LAN, and external
   HTTPS route rules.
3. Keep treasury, recognition, service identity, and current health in separate
   fields and UI lines.
4. Stop unsafe sends before proof export when the recipient cannot reach an
   internal-only mint.
5. Replace the HTTPS heuristic with identity-based multi-route resolution when
   that resolver is available.
6. Allow FIPS and federation paths to produce `Local` or `Across networks`
   according to the boundary crossed, without changing the user terminology.
7. Add acceptance policy only when Safebox has explicit wallet or
   community-authored evidence to support it.

## Related Notes

- [Clear Transfer Routing and Reachability](CLEAR-TRANSFER-ROUTING-AND-REACHABILITY.md)
- [Local Clear Transactions](LOCAL-CLEAR-TRANSACTIONS-DESIGN-NOTE.md)
- [Invariant Identity and Dynamic Resolution](INVARIANT-IDENTITY-AND-DYNAMIC-RESOLUTION.md)
- [Address Spaces, Endpoint Scopes, and FIPS](ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md)
- [Service Identity and Operator Attestation](SERVICE-IDENTITY-AND-OPERATOR-ATTESTATION-DESIGN-NOTE.md)
- [Ecosystem Responsibility Boundaries and Iterative Development](ECOSYSTEM-RESPONSIBILITY-BOUNDARIES-AND-ITERATION.md)
- [Clear CMU Transferability, Acceptance, and Authority](https://github.com/trbouma/clear/blob/main/docs/CMU-TRANSFERABILITY-ACCEPTANCE-AND-AUTHORITY.md)
