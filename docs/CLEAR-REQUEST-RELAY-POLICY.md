# Clear request relay policy

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
