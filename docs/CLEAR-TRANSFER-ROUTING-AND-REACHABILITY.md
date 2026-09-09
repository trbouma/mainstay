# Clear Transfer Routing and Reachability

## Status

Implemented interim profile and manually validated on September 6, 2026.
Multi-route mint identity resolution remains future work.

## Result

Clear transfers now feel like one wallet operation while preserving two
independent routing decisions:

```text
recipient npub -> internal or external inbox relay
Clear keyset   -> internal-only or public mint route
```

The recipient's `npub` and the complete Clear keyset ID are stable identities.
NIP-05 addresses, relay URLs, and mint URLs are mutable discovery and transport
hints.

## Routing Matrix

| Recipient | Mint route | Current result |
| --- | --- | --- |
| Same Mainstay instance | Internal HTTP mint | Send through internal Spurline |
| Same Mainstay instance | Public HTTPS mint | Send through internal Spurline |
| Different Mainstay instance | Public HTTPS mint | Send through external inbox relay |
| Independent Safebox | Public HTTPS mint | Send through external inbox relay |
| Different or independent instance | Internal HTTP mint | Reject before proof export |

Recipient reachability and mint reachability are deliberately separate. A
gift-wrapped token can reach a remote Acorn while still being unusable there if
the issuing mint cannot be reached for proof verification and refresh.

The user-facing transfer labels and their separation from acceptance and
treasury authority are defined in
[Clear Transfer Scope, Acceptance, and Authority](CLEAR-TRANSFER-SCOPE-ACCEPTANCE-AND-AUTHORITY.md).

## Same-Instance Flow

Safebox Web identifies a same-instance recipient when the NIP-05 domain matches
the current application hostname and the handle exists in its local directory.
It resolves the recipient `npub` and stored home relay without DNS or HTTPS,
then passes the internal relay explicitly to Acorn.

For the managed profile, delivery uses `ws://spurline:8080` and mint operations
use `http://clear:3339`. The internal mint address is not included in public
NIP-05 metadata.

## External Flow

For another Mainstay or independent Safebox, the sender resolves NIP-05 over
HTTPS. The advertised relay is a discovery location for the recipient's signed
NIP-17 kind `10050` inbox record. Acorn sends to the relay list controlled by
that recipient record.

A well-formed HTTPS Clear mint URL is provisionally treated as publicly
reachable. The receiver may learn that mint from its first transfer; it does
not need to pre-enroll or advertise every public mint. The receiver still has
to advertise compatible Clear transport support, and any advertised CMU unit
restriction is respected.

## Interim Guard

An external send from an HTTP mint such as `http://clear:3339` is rejected
before Safebox asks Acorn to export proofs. This prevents an internal Mainstay
CMU from being stranded in a wallet that cannot reach its issuer.

This guard distinguishes routes by their current URL form. It does not yet
prove network reachability or authenticate several endpoints as the same mint.

Privileged Clear CLI delivery applies the same default guard. For deliberate
operator distribution inside one Mainstay context, `clear-root send` and
`clear-treasury send` permit an internal mint only when both
`--allow-internal-mint-delivery` and an explicit internal `--relay` are
provided. The override is an operator assertion of shared mint access; it is
not automatic reachability evidence.

## Configuration

Mainstay supplies both mint classes to Safebox for local wallet operation:

```env
SAFEBOX_CLEAR_MINTS=http://clear:3339,https://clear.safebox.dev
```

Only known public routes are included in NIP-05 capability metadata:

```env
SAFEBOX_CLEAR_EXTERNAL_MINTS=https://clear.safebox.dev
SAFEBOX_NIP05_EXTERNAL_RELAYS=wss://spurline.safebox.dev
```

`SAFEBOX_CLEAR_EXTERNAL_MINTS` is informative rather than exhaustive. An
unknown HTTPS mint may still arrive in a valid Clear transfer and be evaluated
when the recipient explicitly accepts it.

## Validation

The following field tests have succeeded:

1. A Clear transfer using the managed internal mint between two wallets in one
   Mainstay instance.
2. A Clear transfer from an independent Safebox to a wallet running under
   Mainstay using the public Clear mint and external relay path.

Automated Safebox Web coverage verifies local directory routing, internal relay
selection, public HTTPS mint discovery, NIP-05 capability checks, and rejection
of external sends from an internal HTTP mint.

## Remaining Work

Multi-reachability will replace the URL-form assumption with:

```text
complete keyset ID
    -> authorized Clear mint-service npub
    -> verified internal, local, external, or FIPS endpoints
```

Several routes may represent one mint only when they serve the same keysets and
shared issuance and spent-proof state. Endpoint verification, succession,
expiry, audience-aware disclosure, and active reachability probing remain part
of that later resolver.

## References

- [Local Clear Transactions](LOCAL-CLEAR-TRANSACTIONS-DESIGN-NOTE.md)
- [Clear Transfer Scope, Acceptance, and Authority](CLEAR-TRANSFER-SCOPE-ACCEPTANCE-AND-AUTHORITY.md)
- [Address Spaces, Endpoint Scopes, and FIPS](ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md)
- [Identity, Resolution, and Event-Native Services](IDENTITY-RESOLUTION-AND-EVENT-NATIVE-SERVICES.md)
- [Safebox Clear Receive Advertisement](https://github.com/trbouma/safebox-web/blob/main/docs/CLEAR-RECEIVE-ADVERTISEMENT.md)
