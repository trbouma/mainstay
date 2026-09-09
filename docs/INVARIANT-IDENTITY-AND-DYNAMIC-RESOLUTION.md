# Invariant Identity and Dynamic Resolution

## Status

This note records an architectural conclusion learned through the Mainstay
prototype. It describes the capability already emerging across Mainstay,
Safebox, Acorn, Clear, Grove, and Spurline, and sets the direction for future
resolution and FIPS work. It does not claim that every resolution record is
already signed, that every service supports multiple routes, or that current
HTTP and DNS compatibility paths can yet be removed.

## The Conclusion

> Mainstay treats identity as invariant and reachability as replaceable.

Here, **reachability** is deliberately narrow: it means the network path a
caller can use from its current scope. **Availability** is the broader security
and operating outcome that an authorized person can obtain and use the service
or information when needed. Dynamic resolution supports availability by
finding an eligible reachable route; it does not make the two terms synonyms.

A service remains the same service when its network location changes. A record,
wallet, currency, or relay relationship also retains its identity when a
different path is required to reach the responsible service.

This separation is a fundamental digital-resilience capability. It allows
Mainstay to reduce mandatory dependence on global DNS, public IP reachability,
and continuous Internet availability without requiring the system to become
isolated. The Internet becomes one available route rather than the foundation
on which identity depends.

## Why Location Is Not Identity

Conventional applications often store a URL as though it answers two questions
at once:

1. What service or resource is this?
2. How can I reach it now?

That coupling is convenient until the domain expires, an address changes, a
service moves, a public connection fails, or the same service is available by
different routes to different callers. The URL then changes even though the
service, resource, authority, or relationship has not.

Mainstay separates the answers:

| Layer | Question | Examples |
| --- | --- | --- |
| Stable identifier | What object or authority is being requested? | wallet `npub`, service `npub`, Clear keyset ID, Grove ciphertext hash |
| Service identity | Which cryptographic service is responsible? | Clear, Grove, Spurline, or Safebox Web service `npub` |
| Capability | What operation does the service support? | mint, relay, blob retrieval, payment provider |
| Reachability | Which path can this caller use now? | Docker address, LAN route, public HTTPS, VPN, FIPS |
| Evidence and policy | Why may this binding and route be trusted? | observed identity, Mainstay context, commissioning evidence, signed descriptor |

The layers are related but must not be collapsed. A Clear keyset ID identifies
an issuance keyset, not its current mint URL. A Grove ciphertext digest
identifies exact bytes, not the server currently retaining them. A service
`npub` identifies a service role, not its host, operator, or transport.

## Resolution Model

The practical model is:

```text
stable identifier
    -> responsible service identity
    -> required capability
    -> routes valid for the caller's context
    -> verified reachable route
```

Mainstay supplies an initial local context because it knows which services it
launched and which private routes belong to the installation. An Acorn retains
portable identifiers and relay-backed mappings so it can resolve outside that
initial context or learn a replacement hint later.

The selected route depends on audience and current topology:

- co-resident containers prefer internal service names;
- nearby clients may use a LAN or trusted VPN route;
- independent deployments may use an external HTTPS or WebSocket endpoint;
- future deployments may select a FIPS-derived or FIPS-native route; and
- an unavailable or ineligible route must fail closed for value transfer rather
  than silently leak an internal address or send unusable proofs.

Dynamic does not mean arbitrary. A newly discovered endpoint is only a
candidate until its identity, capability, scope, and applicable authority
evidence satisfy policy. Context hints enable operation; signed resolution and
commissioning evidence can provide stronger assurance.

## What Mainstay Has Demonstrated

The prototype has made this model concrete rather than merely theoretical:

- Clear balances remain bound to complete keyset identity while internal and
  external mint routes are treated as reachability information.
- Clear transfer guards prevent an internal-only mint route from being sent to
  a recipient that cannot be assumed to reach it, while allowing an explicit
  same-context override.
- Grove-backed records can retain a ciphertext digest and Grove service `npub`
  without redundantly preserving the original URL. Acorn resolves the current
  Grove endpoint when retrieving the attachment.
- Spurline and Safebox transfer behavior can choose internal or external inbox
  relays according to whether the recipient shares the Mainstay context.
- Clear, Grove, Spurline, Safebox Web, and the Mainstay installation expose
  stable service identities independently of their current addresses.

These cases revealed a useful implementation rule: application behavior must
test for the stable reference that establishes the object's existence, not for
the presence of a legacy URL field. A URL may be absent precisely because the
route is intended to be resolved at use time.

## Resilience Properties

Identity-based resolution supports several kinds of continuity:

### Topology continuity

A service can move among containers, hosts, jails, networks, and transports
without forcing every durable record to be rewritten.

### Connectivity continuity

Local services can remain usable when global DNS or an upstream Internet path
is unavailable. When wider connectivity returns, the same identities can be
reached through external routes and synchronized.

### Deployment continuity

An independently operated service and a Mainstay-managed service can implement
the same identity and capability contract even though their installation and
addressing differ.

### Federation without centralization

A Mainstay instance can operate as an autonomous venue while retaining the
ability to discover and communicate with other Mainstay or independent
instances. Federation adds routes and relationships; it does not require a
single global host to become the authority for every participant.

### Recovery continuity

Restoring data, keys, and service identities into a new runtime preserves the
meaning of the installation. New addresses can be published or supplied by the
new context without inventing replacement service identities.

## Relationship to DNS and the Public Internet

The goal is not to ban DNS, HTTPS, or public IP addresses. They remain valuable
compatibility and reachability mechanisms, especially for browsers, LNURL, and
independent services. The goal is to remove the assumption that a domain name
is the durable identity or that a public Internet route is the only usable
path.

Mainstay should therefore:

1. store stable identifiers in durable application records;
2. resolve endpoints as late as practical;
3. retain multiple scoped routes when services support them;
4. avoid exposing internal routes to recipients outside their context;
5. verify that a selected route serves the expected identity and capability;
6. cache enough verified resolution state for useful local operation; and
7. treat public endpoints as replaceable advertisements, not permanent names.

## Relationship to FIPS

FIPS fits this model because it derives network reachability from Nostr key
material. Mainstay's stable service `npub` remains meaningful while FIPS offers
an additional route to that service, either through its IPv6 adapter or a
future native protocol integration.

FIPS is not a fourth endpoint scope. A FIPS route may be internal, local, or
external according to its audience and policy. The FIPS IPv6 adapter also
requires deterministic `.fips` name-to-address translation by the FIPS DNS
source. That local translation is not global DNS discovery and generates no
resolution traffic, but it remains a required part of that adapter path.

Mainstay should begin by carrying FIPS reachability beside existing HTTP and
WebSocket routes. Protocol semantics and stable service identities should not
change merely because FIPS replaces the underlying route.

## Boundaries and Remaining Work

The current implementation is an important proof of the model, not its final
form. Remaining work includes:

- generalized multi-reachability records for mints and other services;
- signed, relay-backed service descriptors and resolution evidence;
- freshness, revocation, key-rotation, and endpoint-expiry rules;
- deterministic conflict handling when resolvers return different routes;
- offline cache policy and operator-readable provenance;
- continuity coordination and replication across Mainstay instances; and
- practical FIPS transport integration.

Until those controls exist, Mainstay context records are useful routing hints
and scoped configuration, not universal proof that any advertised endpoint is
authorized by the service operator.

## Related Notes

- [Identity, Resolution, and Event-Native Services](IDENTITY-RESOLUTION-AND-EVENT-NATIVE-SERVICES.md)
- [Address Spaces, Endpoint Scopes, and FIPS](ADDRESS-SPACES-ENDPOINT-SCOPES-AND-FIPS.md)
- [Service Identity and Operator Attestation](SERVICE-IDENTITY-AND-OPERATOR-ATTESTATION-DESIGN-NOTE.md)
- [Mainstay Grove Context Integration](MAINSTAY-GROVE-CONTEXT-INTEGRATION.md)
- [Clear Transfer Routing and Reachability](CLEAR-TRANSFER-ROUTING-AND-REACHABILITY.md)
- [Mainstay Continuity Coordinator](MAINSTAY-CONTINUITY-COORDINATOR-DESIGN-NOTE.md)
