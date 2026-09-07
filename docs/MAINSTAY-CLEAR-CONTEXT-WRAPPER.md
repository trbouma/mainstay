# Mainstay Clear Context Wrapper

## Status

The first host-side wrapper is implemented by `mainstay-local clear send`. It
automates a privileged local distribution from the managed Clear root wallet
only after resolving the recipient through the co-resident Safebox directory.

This is a narrow operator facility. It is not a general replacement for the
Clear CLI, a wallet owned by Mainstay, or permission to send internal-mint
tokens to arbitrary NIP-05 addresses.

## Purpose

`clear-root` is deliberately independent of Mainstay. It knows its wallet,
mint, recipient, and relay, but it cannot infer that a recipient address is
served by the same Mainstay instance. Its default internal-mint guard therefore
requires an explicit override.

Mainstay has the missing deployment context. It knows the managed Clear and
Spurline routes and can query its local Safebox handle directory. The wrapper
uses that context to make a common local operation concise without weakening
the standalone Clear safety policy.

```bash
poetry run mainstay-local clear send 20 awaycastle559 --memo "hello"
```

Only a bare local handle is accepted. A value containing `@` is rejected so an
external NIP-05 address cannot be accidentally reinterpreted as a local user.
The standard command uses Mainstay's current built-in service registry. A
customized deployment can select its registry with `--config <path>`.

## Ownership Boundary

The root wallet continues to belong to Clear and remains at:

```text
/app/data/clear-root-wallet.json
```

That path is inside the project-scoped `clear-data` volume. Mainstay does not
read, copy, or persist the root wallet. It invokes `clear-root` inside the
managed Clear container and supplies only context-derived command arguments.

This makes Mainstay a context and lifecycle wrapper around `clear-root`, not a
second treasury implementation.

## Eligibility Check

Before proofs are exported, the wrapper:

1. Requires a syntactically valid bare handle.
2. Queries the local Safebox endpoint registered with `local` scope.
3. Requires that exact handle in the NIP-05 `names` map with a valid public key.
4. Requires the handle's Clear descriptor to advertise
   `clear-token-transfer`, NIP-59, and event kind `7379`.
5. Requires enabled internal Clear and Spurline services in the Mainstay
   registry.

These checks prove that the destination is a locally registered Safebox capable
of receiving a Clear transfer. They do not prove that every external address
using the same domain is local, which is why full NIP-05 addresses are outside
this command's contract.

## Command Translation

After eligibility succeeds, Mainstay resolves the recipient to its hex public
key and executes the equivalent of:

```bash
docker compose exec -T clear clear-root send 20 <recipient-pubkey> \
  --allow-internal-mint-delivery \
  --relay ws://spurline:8080 \
  --memo "hello"
```

Using the public key prevents `clear-root` from performing external NIP-05
resolution. The internal relay comes from the Mainstay registry rather than
user input. Operators can select a Compose or environment file, but cannot use
this wrapper to substitute a different relay or bypass local recipient checks.

## Output and Failure Handling

The wrapper emits a compact receipt containing the amount, CMU, mint route,
recipient, event ID, and relay verification state. It never repeats bearer
tokens or proof secrets from `clear-root` on its own output.

Failures before `clear-root` starts are safe to correct and retry. A non-zero
`clear-root` exit is reported as a failed operation. If `clear-root` exits
successfully but its receipt cannot be parsed, Mainstay reports an uncertain
outcome and tells the operator not to retry until the root wallet has been
reconciled.

## Scope and Future Work

The first wrapper covers root-wallet distribution to one Safebox registered in
the same Mainstay instance. It does not cover treasurer wallets, cross-Mainstay
delivery, external recipients, multi-reachability mint resolution, or arbitrary
token import.

As service identity and signed relay-backed records mature, local eligibility
should bind the recipient, Clear mint-service identity, keyset ID, and Spurline
service identity cryptographically. The CLI shape can remain stable while URL
lookups become identity-based resolution.
