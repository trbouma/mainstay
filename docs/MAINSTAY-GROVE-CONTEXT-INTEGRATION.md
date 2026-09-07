# Mainstay Grove Context Integration

Mainstay supplies deployment context; it does not become the owner of wallet
records. The control plane exposes a read-only `/context` manifest containing
the Mainstay installation `npub`, the Grove service `npub` reported by Grove,
and Grove's scoped internal Blossom endpoint. No service or installation
`nsec` is returned.

Safebox Web reads this manifest from the private Docker network. For each
Acorn, it sets the active Mainstay context and asks Safebox Acorn to install the
Grove route in the wallet's encrypted, relay-backed `context_endpoints` record.
The operation is idempotent and preserves unrelated endpoint hints.

This gives records stable provider identity while retaining local routing:

```text
record blob_service_npubs
        |
        v
Grove service npub + active Mainstay installation npub
        |
        v
http://grove:8000 inside this Mainstay network
```

An internal route is eligible only while the Acorn is operating in the
matching Mainstay context. A future signed external Grove descriptor or FIPS
endpoint can be added for the same service `npub` without rewriting stored
records or changing blob hashes.

The first implementation treats Mainstay's route as a candidate supplied over
the trusted local network. Signed context manifests and independently verified
service descriptors remain later hardening steps.
