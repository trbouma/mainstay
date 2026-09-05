# Address Spaces, Endpoint Scopes, and FIPS

## Status

This note defines how Mainstay describes service reachability without making a
domain name, IP address, container name, or FIPS locator part of the service's
durable identity. It documents the endpoint model implemented in
`mainstay-local` and the intended evolution toward FIPS.

The central rule is:

> Scope describes who may use an endpoint. Transport describes how to reach it.

Internal, local, and external are scopes. HTTP, WebSocket, IPv4, IPv6, DNS, and
FIPS are transports or locator forms. These dimensions must remain separate.

## Why Separate Identity and Address

A service can move without becoming a different service. Docker DNS names,
FreeBSD jail addresses, LAN addresses, public domains, and FIPS node addresses
may all change over its lifetime.

For Clear, the complete keyset ID is the stable identity of a CMU. A mint URL
carried in a token is a routing hint. Mainstay may associate several verified
routes with a keyset without treating any one route as the keyset's identity.

The same separation applies elsewhere:

- a Spurline relay has service identity distinct from its WebSocket address;
- a Grove server has service identity distinct from its HTTP origin;
- a Safebox application instance has identity distinct from its browser URL;
- a FIPS node has a cryptographic npub identity and may also have derived or
  adapted network addresses.

## Reachability Scopes

### Internal

An internal endpoint is private to one Mainstay runtime boundary.

Examples include:

- a Docker Compose network name such as `http://clear:3339`;
- a loopback socket shared by processes in one jail;
- a Unix socket or jail-local address;
- a private FIPS route used only among services in one deployment.

Internal endpoints are the preferred routes for communication among
co-resident Mainstay services. Safebox Web and Safebox Acorn should receive
these routes for Clear, Grove, and Spurline while running in the same bundle.
Internal endpoints must not be presented as usable routes to another machine.

### Local

A local endpoint is deliberately made available to trusted clients near the
deployment but is not intended as a generally public route.

Examples include:

- a host port bound to a LAN interface;
- an address reachable through a trusted VPN;
- a local reverse-proxy route;
- a FIPS route shared with a defined local community or peer set.

`local` is a policy boundary, not a synonym for loopback. A loopback-only
address can be local to the host, but it is not reachable by another machine.
Mainstay must not infer local exposure merely because a host port exists; the
operator must configure the endpoint deliberately.

### External

An external endpoint is intended to be reachable beyond the local operational
environment.

Examples include:

- `https://mint.safebox.dev`;
- a public relay WebSocket URL;
- an internet-routable IP address;
- a FIPS service intentionally discoverable by remote mesh participants.

External does not necessarily mean untrusted or unencrypted. Authentication,
authorization, and encryption remain separate properties. It means only that
the route crosses the local trust and administration boundary.

## Current Mainstay Schema

The current registry represents an endpoint as:

```yaml
scope: internal | local | external
purpose: web | mint | blossom | relay | service
url: <transport-specific URL>
priority: <integer>
```

For example:

```yaml
services:
  clear:
    kind: clear-mint
    endpoints:
      - scope: internal
        purpose: mint
        url: http://clear:3339
        priority: 10

  lightning_mint:
    kind: cashu-lightning-mint
    endpoints:
      - scope: external
        purpose: mint
        url: https://mint.safebox.dev
        priority: 10

  external_clear_mint:
    kind: clear-mint
    endpoints:
      - scope: external
        purpose: mint
        url: https://clear.safebox.dev
        priority: 10
```

Lower priority numbers are preferred within the same scope and purpose.
Purpose prevents Mainstay from confusing different interfaces exposed by one
service, such as a public protocol endpoint and an operator interface.

The current `url` field is sufficient for HTTP and WebSocket services. It is an
intermediate representation rather than the final FIPS model.

## Selection Rules

Mainstay selects endpoints according to the caller and purpose.

### Co-resident service calls

Safebox and other services inside the bundle must use an endpoint with
`scope: internal`. Mainstay must not silently replace it with a local or
external route merely because that route has a lower numeric priority.

This rule applies to co-resident dependencies such as Clear, Grove, and
Spurline. An Acorn's Lightning-backed home mint is a different service class:
it is external to Mainstay and defaults to `https://mint.safebox.dev`. The
internal Clear mint appears only in Safebox's Clear-specific configuration.

Mainstay currently supplies `https://clear.safebox.dev` as the default
external Clear discovery endpoint alongside the managed internal Clear mint.
Adding this route authorizes Safebox to request its keyset metadata; it does
not make the URL a currency identity or make different CMUs interchangeable.
Mainstay must retain every discovered `cmu-<keyset-id>` as a separate balance
and eventual acceptance decision.

### Routing hints produced by a service

When a service must publish a route for a token, document, or protocol response,
Mainstay currently prefers scopes in this order:

1. external;
2. local;
3. internal.

This allows an internal Clear API connection and an external token routing hint
to coexist. If Clear has no published route, its internal endpoint remains the
development fallback. Production commissioning should make that fallback an
explicit operator decision.

### Dashboard display

The dashboard shows only endpoints present in the registry:

- internal endpoints are displayed as diagnostic addresses, not browser links;
- local HTTP endpoints may be presented as links and adjusted from loopback to
  the Mainstay host used by the browser;
- external HTTP endpoints are presented exactly as configured;
- an absent scope produces no placeholder address.

Health and homepage probes are control-plane diagnostics. They currently have
explicit URLs and normally use the internal runtime namespace. They do not by
themselves publish a service into the local or external scope.

## Payment Identity and Discovery

Mainstay must keep payment identity separate from payment discovery and
settlement. An Acorn's Nostr public key is its durable identity. A domain name,
Lightning address, LNURL endpoint, mint URL, IP address, or FIPS locator is a
route or discovery hint associated with that identity; none should silently
replace it.

A local Safebox can receive Lightning payments without advertising a Lightning
address. It can request an invoice from its configured external
Lightning-backed mint, present that invoice directly, and let the service Acorn
complete settlement and recipient delivery. This path depends on the external
mint but does not require the local Safebox instance to own a public DNS name
or HTTPS certificate.

A conventional Lightning address is a separate convenience interface. An
address such as `alice@example.org` requires DNS resolution and an externally
reachable HTTPS `/.well-known/lnurlp/alice` endpoint. It is useful for
interoperability with existing wallets, but it introduces domain and
certificate lifecycle dependencies that are not necessary for local invoice
receipt. Mainstay should therefore treat a Lightning address as optional
external discovery metadata, not as the Acorn identity or a prerequisite for
receiving payments.

Future payment discovery may include several parallel routes:

- a directly presented Lightning invoice;
- an optional DNS and HTTPS Lightning address;
- a Nostr request addressed to an Acorn or service `npub`;
- a FIPS IPv6-adapter route associated with an `npub`; and
- a native FIPS locator when that application interface is stable.

The current implementation intentionally does not introduce a public Safebox
base URL or Lightning-address domain setting. Before adding one, the design
must decide how an advertised payment endpoint is bound to an Acorn or service
identity, how that binding is verified, and how non-DNS discovery coexists
with conventional LNURL clients. FIPS is expected to reduce location coupling,
but it does not by itself redefine the Lightning address protocol or remove
the need for a compatibility gateway when an ordinary Lightning wallet expects
DNS and HTTPS.

## How FIPS Fits

FIPS is not a fourth scope. It is an identity-aware network and transport path
that may carry an internal, local, or external endpoint.

FIPS uses Nostr keypairs as node identities. Applications may identify a node
by pubkey or npub. The protocol derives a node address for routing and an
`fd00::/8` IPv6 overlay address for the TUN adapter. Existing HTTP and
WebSocket applications can use the IPv6 adapter, while FIPS-aware applications
may eventually use the native datagram API directly.

This creates at least two practical FIPS integration paths for Mainstay.

### IPv6 adapter path

An existing service continues to use its normal protocol over a FIPS-derived
IPv6 address or an `npub...fips` name:

```yaml
scope: external
purpose: mint
transport: fips-ipv6
url: http://npub1example.fips:3339
```

This path minimizes application changes. Resolving the `npub...fips` name
through the FIPS DNS source is required before traffic is sent to `fips0`. FIPS
deterministically derives the overlay IPv6 address from the npub and primes its
local identity cache during that lookup. The translation is local,
instantaneous, and generates no network or mesh traffic. It is still required
because the derived IPv6 address alone cannot be reversed to recover the npub
needed for routing. The resulting address is an overlay address and should not
be mistaken for an ordinary public IPv6 route.

### Native FIPS path

A FIPS-aware client addresses the destination directly by npub and FSP port:

```yaml
scope: external
purpose: mint
transport: fips-native
locator:
  npub: npub1example
  port: 3339
```

The FIPS native API is currently experimental, so Mainstay should begin with
the IPv6 adapter for unmodified services and retain room for a native locator
later.

## Target Endpoint Representation

Because FIPS locators are structurally different from URLs, the endpoint model
should eventually become a discriminated transport record:

```yaml
endpoints:
  - scope: internal
    purpose: mint
    transport: http
    priority: 10
    locator:
      url: http://clear:3339

  - scope: external
    purpose: mint
    transport: fips-native
    priority: 30
    locator:
      npub: npub1example
      port: 3339
```

Mainstay should not force a native FIPS locator into an invented URL syntax
unless FIPS standardizes one. A structured locator allows validation and
connection logic to depend on `transport` without parsing unrelated address
forms from a string.

The existing service-level `fips_npub` and `fips_port` fields are transitional.
Once FIPS connectivity is implemented, they should move into one or more
scoped endpoint records. This matters because one service may eventually have
different FIPS nodes, ports, priorities, or exposure policies for different
purposes.

## Identity and Verification

Endpoint selection alone is not sufficient. Mainstay must verify that a route
reaches the intended service identity.

For Clear, endpoint verification should include:

1. connect to a candidate route;
2. request the expected keyset;
3. confirm that its complete keyset ID matches the CMU being routed;
4. verify any issuer or root-authority policy required by Clear;
5. use multiple routes for one keyset only when they share authoritative
   issuance and spent-note state or form an explicitly coordinated cluster.

For FIPS, control of the destination npub is authenticated by the FIPS session,
but that node identity still needs an application-level binding to the Clear
keyset, Grove service, or Spurline relay that Mainstay intended to reach.

## Exposure and Security

Adding a local or external endpoint is an operator action. It may require:

- publishing a host port or reverse-proxy route;
- configuring firewall, VPN, or FIPS peer policy;
- enabling TLS or another authenticated transport;
- limiting operator APIs independently from public protocol APIs;
- recording which service identity the endpoint is expected to expose;
- testing the route from the scope in which it is advertised.

Mainstay must not infer exposure from Docker port mappings, debug ports, DNS
records, FIPS reachability, or a successful health check. Reachability and
authorization are related operational facts, but neither establishes the
other.

## Migration

The registry currently accepts the previous fields while deployments move to
scoped endpoints:

- `local_url` becomes an `internal` endpoint;
- `advertised_url` becomes a `local` endpoint.

Newly generated registries emit only the scoped endpoint list. An operator who
previously used `advertised_url` for an internet-facing route should relabel it
as `external` explicitly.

## Near-Term Decisions

Before exposing Clear or Grove beyond one Mainstay instance, decide:

1. whether the first shared route is LAN/VPN-local, public internet, FIPS, or a
   combination;
2. how Mainstay authenticates the binding between a route and service identity;
3. whether local and external traffic reaches services directly or through a
   Mainstay gateway;
4. which protocol interfaces are publishable and which remain internal-only;
5. how route changes are discovered and distributed without making DNS the
   permanent identity anchor.

The final point concerns public or infrastructure DNS as an identity anchor.
It does not remove the required local `.fips` DNS translation used by the FIPS
IPv6 adapter; that resolver is part of FIPS address preparation rather than an
external discovery dependency.

## References

- [FIPS design overview](https://github.com/jmcorgan/fips/blob/master/docs/design/README.md)
- [FIPS architecture and identity](https://github.com/jmcorgan/fips/blob/master/docs/design/fips-architecture.md)
- [FIPS IPv6 adapter](https://github.com/jmcorgan/fips/blob/master/docs/design/fips-ipv6-adapter.md)
- [FIPS native API](https://github.com/jmcorgan/fips/blob/master/docs/design/fips-native-api.md)
