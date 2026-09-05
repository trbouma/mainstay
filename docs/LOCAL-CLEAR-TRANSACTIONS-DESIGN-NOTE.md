# Local Clear Transactions

## Status

This note defines the first Clear transaction profile for Mainstay. It is a
design document only. It does not change Mainstay bootstrap, Clear, Safebox
Web, Safebox Acorn, or the current container configuration.

The first profile is deliberately local-only:

> Transfer one Clear Mint Unit between two Safebox identities in the same
> Mainstay environment, using only Mainstay's internal Clear and Spurline
> routes.

External Clear mint import, public service discovery, FIPS transport, and
cross-Mainstay transfer are later profiles.

## Goal

Two local users should be able to transfer a CMU without DNS, public HTTPS,
Lightning, or direct browser access to infrastructure services.

The users may be connected to the same Safebox Web application or to separate
Safebox Web processes inside one Mainstay environment. Each user is represented
by a distinct Acorn `npub`. Both Safebox processes, when separate, use the same
commissioned internal Clear mint and local Spurline relay.

```text
sender browser                         recipient browser
      |                                      |
      v                                      v
sender Safebox / Acorn                recipient Safebox / Acorn
      |                                      ^
      | NIP-59 Clear transfer               | receive and accept
      +----------> ws://spurline:8080 -------+
      |                                      |
      +----------> http://clear:3339 <--------+
                  validate and refresh
```

Browser location does not determine transaction locality. A phone connected
through a VPN may be geographically remote while its Safebox and Acorn
operations still execute inside the Mainstay runtime. The transaction is local
because both wallet identities use the same local service environment and the
infrastructure calls remain on internal routes.

## Out of Scope

The first profile does not include:

- accepting CMUs issued by `https://clear.safebox.dev`;
- sending an internal CMU to another Mainstay installation;
- exposing the internal Clear or Spurline ports to a LAN or the internet;
- converting Clear value to Cashu cash or Lightning;
- automatic exchange between different CMUs;
- public NIP-05 or DNS-based recipient discovery;
- FIPS routing;
- event-native replacements for the existing Clear REST API; or
- automatic acceptance of a received bearer token.

Keeping external Clear support out of the first profile does not reject that
capability. It prevents external trust, routing, and interoperability questions
from obscuring the local transaction invariant.

## Local Context

A Clear transaction qualifies as local when all of the following are true:

1. Sender and recipient are Acorn identities registered in the same Mainstay
   environment.
2. Both resolve their home relay to the same managed Spurline service identity.
3. The transferred proofs belong to a CMU issued by the managed local Clear
   mint.
4. The complete keyset ID resolves to that managed Clear mint-service identity.
5. Both wallets can reach the mint through `http://clear:3339` from inside the
   runtime.
6. Transfer delivery uses `ws://spurline:8080`.
7. No external fallback is attempted when an internal dependency is
   unavailable.

During the initial URL-based phase, Mainstay may prove conditions 2 and 4 from
its commissioned local registry. Once service identities are implemented,
those comparisons should use Spurline and Clear service `npub`s rather than URL
equality.

## Identity Model

The transaction must retain these independent identities:

| Identity | Meaning |
| --- | --- |
| Sender Acorn `npub` | Author of the transfer |
| Recipient Acorn `npub` | Intended receiver |
| Spurline service `npub` | Relay used for local delivery |
| Clear mint-service `npub` | Service responsible for validation and refresh |
| Complete keyset ID | Issuance keyset represented by the proofs |
| `cmu-<keyset-id>` | Canonical Clear Mint Unit |
| Currency root | Authority that commissions the currency and mint service |

The internal URLs are routes:

```text
ws://spurline:8080 -> local Spurline service identity
http://clear:3339  -> local Clear mint-service identity
```

They are not copied into the identity layer. The token may continue to carry a
mint URL for Cashu compatibility, but the local registry and complete keyset ID
determine which configured route Safebox is permitted to use.

## Preconditions

Before non-disposable local value is transferred:

- Clear root commissioning has been completed manually;
- the local CMU and complete keyset ID are known;
- the local mint-service identity has been generated and bound to that
  currency when the identity feature exists;
- Mainstay records the internal Clear and Spurline routes;
- sender and recipient Acorns use the local Spurline relay;
- the sender holds spendable proofs for the exact local CMU; and
- the recipient advertises or locally registers support for that CMU.

An uncommissioned development mint may be used for disposable testing, but the
UI and registry must identify it as uncommissioned.

## Recipient Resolution

Local recipient discovery must not call:

```text
https://<local-address>/.well-known/nostr.json
```

Safebox Web should resolve an address served by the current Mainstay instance
from its local claimed-handle directory. The result supplies:

```yaml
recipient:
  npub: npub1recipient...
  home_relay_identity: npub1spurline...
  clear_receive:
    protocols: [clear-token-transfer]
    cmus: [cmu-<local-keyset-id>]
```

If separate Safebox Web processes participate in one environment, Mainstay
needs a shared or signed local directory that provides the same information.
Sharing a database is not required if the directory records are signed and
resolvable through local infrastructure.

The sender must establish all of the following before exporting proofs:

- the recipient `npub` is valid;
- the recipient is bound to the managed local Spurline identity;
- the recipient supports Clear token transfer;
- the recipient accepts the exact local CMU; and
- the sender is not relying only on a user-entered URL or unverified handle.

Failure to establish local eligibility stops the operation. It does not fall
back to Lightning, ordinary ecash, or an external Clear mint.

## Transaction Sequence

### 1. Prepare

Safebox shows the exact recipient, amount, CMU, keyset ID, and local mint
identity. The user explicitly confirms a Clear transfer. Friendly labels may
be displayed, but the canonical CMU remains visible.

### 2. Export

The sender Acorn asks the internal Clear route to swap its existing proofs into
the requested transfer amount and any required change. The exported token is
bound to one mint and one CMU. Sender history records the operation and the
proof events created and destroyed.

### 3. Deliver

The sender Acorn encrypts the Clear token to the recipient `npub` and publishes
the NIP-59 gift wrap to internal Spurline. Relay acceptance confirms transport
only; it does not prove recipient acceptance.

The current protocol shape remains:

```text
outer event: NIP-59 gift wrap
inner kind: 7379
protocol: clear-token-transfer
```

### 4. Receive

The recipient Acorn scans internal Spurline, decrypts the message, validates
the recipient binding and payload shape, and stores a pending Clear receipt.
Discovery must not mutate spendable balance automatically.

### 5. Accept

The recipient explicitly accepts the pending receipt. Acorn verifies that the
token contains one mint, the expected local CMU, and the complete local keyset
ID. It selects `http://clear:3339` from Mainstay's local registry, verifies the
keyset served there, and refreshes the bearer proofs into recipient-owned proof
state.

### 6. Record

The recipient stores the accepted proof state and Clear transaction history.
The bearer token is erased from the pending receipt. The balance remains
grouped under the exact local CMU and keyset ID.

## Routing Rules

The local profile uses fixed scope selection:

| Purpose | Required scope | Initial route |
| --- | --- | --- |
| Recipient transfer delivery | Internal | `ws://spurline:8080` |
| Keyset discovery | Internal | `http://clear:3339/v1/keys` |
| Proof swap and refresh | Internal | `http://clear:3339` |
| Safebox user interface | Local | `http://<mainstay-host>:8888` |

An internal failure remains visible. Mainstay must not silently choose
`https://clear.safebox.dev` because the internal Clear mint is unavailable;
that external service has different keysets and cannot validate or refresh the
local proofs.

Likewise, an internal Spurline failure leaves delivery pending or failed. It
must not silently publish the bearer transfer to an external relay without an
explicit policy and renewed user confirmation.

## Trust and Safety

The first profile uses a closed trust policy:

```text
accepted Clear service: managed local Clear only
accepted keysets: commissioned local keysets only
accepted CMUs: explicit local CMUs only
accepted relay: managed local Spurline only
unknown token policy: reject or quarantine without network access
```

The token's embedded mint URL is advisory. Acceptance must never use it to
contact an arbitrary host. The selected internal endpoint must come from the
commissioned Mainstay registry and must serve public keys that reproduce the
token's complete keyset ID.

Sender and recipient actions are independently authenticated. The relay cannot
create a valid sender event, and the mint cannot select the intended recipient.
The recipient retains explicit control over acceptance.

## Failure Semantics

The UI and transaction state should distinguish:

- **pre-export failure:** no sender proofs were changed; retry may be safe;
- **export outcome unresolved:** do not retry blindly; reconcile sender proof
  and history state;
- **delivery failed:** exported bearer value remains sender-controlled only if
  Acorn can prove it was not published or can safely recover it;
- **delivery accepted by relay:** recipient acceptance is still pending;
- **recipient mint unavailable:** retain the pending token and retry acceptance
  later against the same internal mint;
- **inputs already spent during acceptance:** recover relay-backed replacement
  proof state before deciding the outcome; and
- **wrong keyset, CMU, relay, or mint identity:** fail closed without external
  fallback.

No aggregate status such as `payment failed` should erase which phase became
uncertain.

## Current Implementation Fit

The existing repositories already provide much of the transaction path:

- Mainstay keeps Clear and Spurline on private Compose routes.
- Safebox Web separates Clear balances from ordinary cash balances.
- Safebox Acorn exports an exact Clear token, sends it in a NIP-59 gift wrap,
  stores pending receipts, and refreshes accepted proofs.
- Clear serves keyset metadata and swap operations on the internal network.
- receipt acceptance is explicit and runs as a durable Safebox Web background
  job.

The important gaps for this local profile are:

1. Safebox's Clear-recipient resolver currently performs HTTPS NIP-05 lookup;
   it needs the same local-directory path used for local Lightning recipients.
2. The local Clear mint does not yet expose and persist the proposed
   mint-service identity.
3. Mainstay cannot yet resolve a keyset ID to that service identity and its
   internal route.
4. `SAFEBOX_CLEAR_MINTS` currently combines receive advertisement and metadata
   routing; it is not a complete local trust policy.
5. Acorn acceptance currently follows the mint URL carried in the token rather
   than receiving a pre-verified route selected by Mainstay or Safebox.
6. Public NIP-05 capability output can include the private Docker mint URL when
   it is present in `SAFEBOX_CLEAR_MINTS`.

These are future implementation tasks, not changes made by this note.

## First Implementation Slices

When implementation begins, use narrow slices:

1. Define the local Clear transaction fixture with two Acorn identities, one
   Spurline instance, one commissioned keyset, and one internal Clear route.
2. Add local Clear recipient resolution without HTTPS or DNS.
3. Separate local receive policy from externally published NIP-05 metadata.
4. Add the Clear mint-service identity and startup mismatch sentinel.
5. Bind the commissioned local keyset to that identity.
6. Add keyset-to-service resolution and internal endpoint selection.
7. Change Acorn acceptance to use the verified selected route while retaining
   the token URL as provenance.
8. Exercise send, pending receipt, explicit acceptance, restart recovery, and
   failure states end to end.

Only after this profile is reliable should Mainstay add an external-token
acceptance profile for `https://clear.safebox.dev`.

## Acceptance Criteria

- Two local Acorns can transfer the commissioned local CMU end to end.
- All mint and relay traffic stays on the Compose network.
- Neither browser needs direct access to Clear or Spurline.
- DNS, public HTTPS, Lightning, and external mints are not contacted.
- The receiver must explicitly accept the pending transfer.
- Sender and recipient histories identify the exact CMU and keyset ID.
- Mainstay never combines balances across keysets or CMUs.
- Internal dependency failure does not trigger an external fallback.
- A token naming an unknown keyset or arbitrary mint URL causes no outbound
  request.
- Restart and uncertain-outcome handling do not duplicate or lose value.

## References

- [Identity, Resolution, and Event-Native Services](IDENTITY-RESOLUTION-AND-EVENT-NATIVE-SERVICES.md)
- [Address Spaces, Endpoint Scopes, and FIPS](ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md)
- [Clear Receive Advertisement](https://github.com/trbouma/safebox-web/blob/main/docs/CLEAR-RECEIVE-ADVERTISEMENT.md)
- [Clear authority model](https://github.com/trbouma/clear/blob/main/docs/MULTI-CURRENCY-TREASURER-AUTHORIZATION-DESIGN.md)
