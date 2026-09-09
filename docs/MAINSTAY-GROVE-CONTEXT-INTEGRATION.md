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

## Runtime Resolution

Safebox Web uses `SAFEBOX_MAINSTAY_CONTEXT_URL` to retrieve `/context`. It
caches the public manifest briefly, assigns the installation `npub` as the
Acorn's active context, and periodically checks that the wallet's private
`context_endpoints` record contains the current Grove hint. A standalone
Safebox leaves this setting blank and does not acquire a Mainstay context.

When an attachment operation begins, Acorn resolves the Grove `npub` stored in
the Safebox record. Global service records may contribute only external HTTPS
routes. Context records may contribute internal or local HTTP routes only when
their `context_npub` matches the active Mainstay installation. Eligible routes
are ordered by evidence state, scope, and priority, then deduplicated.

The ordinary local path is therefore:

```text
attachment ciphertext hash
    -> Grove service npub
    -> active Mainstay installation npub
    -> matching context endpoint
    -> http://grove:8000
```

The old `blobref` and configured Blossom servers remain compatibility
fallbacks. For a record that names Grove identities, a fallback server must
report a matching service `npub`. Acorn then independently verifies the
ciphertext hash before decryption and the plaintext hash afterward. Mainstay
selects the local context; it does not replace resource-integrity checks or
take ownership of the wallet's records.

## Consumer Invariant

Applications must treat `blobsha256` as the indication that a record has an
attachment. They must not use `blobref` presence to decide whether to show,
download, preserve, or delete it. For an identity-aware record, an absent
`blobref` deliberately means “resolve the named Grove service now,” not “no
attachment.” The current endpoint may change without rewriting the record.
