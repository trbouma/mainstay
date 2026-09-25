# Clear request relay policy

Shared principles and known limitations live in
[Acorn: Transfer resilience](https://github.com/trbouma/safebox-acorn/blob/main/docs/TRANSFER-RESILIENCE.md).
For pending transfers, monitoring windows, and refresh actions, see
[Safebox Web: Transfer status and recovery](https://github.com/trbouma/safebox-web/blob/main/docs/TRANSFER-STATUS-AND-RECOVERY.md).

Mainstay defaults to `MAINSTAY_CLEAR_REQUEST_RELAY_POLICY=mint-route`.
Safebox Web selects a request inbox from the mint route carried in the
Clear payment request:

- A public HTTPS mint route uses the wallet's public NIP-17 inbox relays.
- A Docker hostname, localhost, private IP, or local hostname uses
  `MAINSTAY_CLEAR_REQUEST_INTERNAL_RELAY` (default `ws://spurline:8080`).

These values can be set in `.env`. Set the policy to `public` to require
public inboxes for every request. Independent Safebox Web installations
default to `public`; their corresponding settings are
`SAFEBOX_CLEAR_REQUEST_RELAY_POLICY` and `SAFEBOX_CLEAR_REQUEST_INTERNAL_RELAY`.

| Deployment | Setting | Default / use |
| --- | --- | --- |
| Mainstay | `MAINSTAY_CLEAR_REQUEST_RELAY_POLICY` | `mint-route`; choose `public` to require public inboxes for all requests. |
| Mainstay | `MAINSTAY_CLEAR_REQUEST_INTERNAL_RELAY` | `ws://spurline:8080`; valid only in the intended deployment network. |
| Standalone Web | `SAFEBOX_CLEAR_REQUEST_RELAY_POLICY` | `public`; internal routing requires explicit `mint-route` configuration. |
| Standalone Web | `SAFEBOX_CLEAR_REQUEST_INTERNAL_RELAY` | Unset by default; required when choosing `mint-route`. |
| Safebox Web | `SAFEBOX_NIP05_EXTERNAL_RELAYS` | Comma-separated public inbox defaults; missing wallet inbox records can be initialized, existing signed records are not overwritten. |

The policy classifies the selected URL using the same availability rules
as the Clear balance display. It does not probe Internet reachability or
infer that two URLs refer to the same mint. A balance using `http://clear:3339`
therefore creates an internal request even if the operator also exposes that
mint through HTTPS. Use its public route for a cross-network request.
Non-HTTPS mint routes are treated as internal by this policy.

Public requests fail when no public wallet inbox is available. They never
fall back to advertising Docker addresses. Public discovery relays are not
automatically treated as wallet inboxes. Internal requests bypass public
inbox discovery, allowing request creation while disconnected.

The selected relay is embedded in the NUT-18 request and retained by its
confirmation monitor. Payers must be able to reach both that relay and the
mint. A Docker-only request is usable by clients inside that network, not
automatically by browsers or wallets elsewhere on the LAN. This policy does
not publish internal addresses in the wallet's public NIP-17 inbox record,
expose management endpoints, or change their authentication.

Deployment requires the Acorn encoder with `allow_internal_relays` support,
Safebox Web's routing settings, and Mainstay's Compose configuration. Publish
the Acorn changes, update Safebox Web's locked Acorn revision, then publish
Safebox Web and rebuild the Mainstay services. Recreate Safebox Web to apply
changes to the environment.

## Operator checks

Route scope is relative to the caller. Same-instance Web containers can use
`ws://spurline:8080`; a separate Mainstay installation may resolve that same name
to its own relay. A LAN client does not automatically share Docker DNS, and
localhost refers to the calling host/container. Public URLs are not guarantees
of availability or proof that they alias an internal service.

For a failed request payment:

1. Confirm whether both wallets' server processes share this Mainstay network.
2. Decode the exact request used, not an earlier test: compare recipient key,
   mint, unit, amount, request ID, and advertised relay.
3. Query the sender's event ID on that relay from inside the relevant network.
   Check the outer recipient tag. Do not substitute an unauthenticated public
   relay lookup for this internal check.
4. If present and correctly addressed, investigate receiver discovery, scan
   failures, and cursor filters before changing routes. If pending, investigate
   acceptance and mint connectivity. A successful sender is not evidence of
   receiver acceptance.
5. Preserve event/receipt references for review. Do not reissue credits, clear
   proof state, or erase checkpoints merely to make a status message disappear.

Use sanitized metadata in diagnostics: event/request IDs, public recipient key,
route, stage, and error category. Never include private keys, proofs, bearer
tokens, or browser authorization tickets in shared logs.

Mainstay does not own a second payment state machine. Route selection and
operator lifecycle belong here; proof safety and recovery belong to Acorn,
and bounded monitoring and user-visible status belong to Safebox Web.
