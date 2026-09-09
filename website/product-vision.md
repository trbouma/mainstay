---
title: Product Vision
description: The product promise, principles, and direction for Mainstay.
---

# Product Vision

**Mainstay is a unified local-first application that keeps essential
information and value available and usable when conditions change.**

It gives individuals, organizations, and communities a dependable place to
manage the information and value they need to continue operating. Hosted
services can assist, but the experience should not disappear when a provider,
mint, or wider network becomes unavailable.

## The product promise

Mainstay should make sophisticated continuity infrastructure feel ordinary:

- records remain available locally;
- confirmed balance and pending value remain visibly distinct;
- payments can be preserved when finalization is unavailable;
- local Clear currencies can operate without Bitcoin or Lightning;
- activity synchronizes and finalizes when services return; and
- one application works across connected, local, mobile, and community modes.

People should not need to understand relays, proof denominations, blob storage,
or synchronization protocols to know what is available and what to do next.

## Identity outlives location

Mainstay treats identity as durable while routes remain replaceable. A service
remains the same service when it moves from a local container to a LAN address,
public endpoint, VPN route, or future FIPS path. Records, wallets, and
currencies likewise retain stable identifiers even when the route to the
service responsible for them changes.

This turns identity-based resolution into a digital-resilience capability.
DNS, HTTPS, and public IP connectivity can remain useful ways to reach a
service without becoming the source of its identity or a requirement for local
operation. Mainstay can use the best eligible route for the present context,
then use another route when conditions change without asking the user to treat
the service as something new.

The goal is not an Internet-free system. It is a system in which the Internet
is one available path rather than the single foundation for identity,
discovery, and continuity. This also lets autonomous Mainstay venues cooperate
across a wider network without surrendering their local authority or depending
on one central host.

## Product principles

1. **Local-first, not local-only.** Use helpful network services without making
   ordinary local operation depend on their continuous availability.
2. **Continuity without ambiguity.** Show what is confirmed, what is pending,
   and what can be finalized later.
3. **The app is not the authority.** Preserve portable records, keys, funds,
   policies, and evidence outside the application boundary.
4. **One experience across modes.** Do not turn disruption into an unfamiliar
   emergency-only product.
5. **Good boundaries, not barriers.** Keep the sibling products separately
   deployable, testable, and replaceable, with clear authority and failure
   boundaries. Use open protocols so separation preserves interoperability
   and continuity rather than obstructing them.
6. **Bounded economies remain bounded.** Never imply that separate Clear
   currencies are interchangeable, universally accepted, or legal tender.
7. **Identity outlives location.** Preserve stable identities and resolve a
   currently eligible path instead of storing one network address as permanent
   truth.
8. **Local stewardship, shared governance.** Give each community or
   organization a dependable place to operate its own documented rules for
   access, recognition, issuance, and reconciliation while remaining connected
   to compatible outside systems.
9. **Security includes availability.** Treat confidentiality, integrity, and
   availability as complementary obligations. A network route is only one
   contributor to keeping authorized services and information usable.

## The product model

```text
Mainstay is the application.
Lockbox is the appliance.
There's no place like home.
```

**Our House. Our Rules. Our Business.** is the governance expression of that
model: local stewardship, accountable procedures, ordinary work, and
appropriate confidentiality within a community's legitimate scope.

Mainstay is the primary user entry point. Lockbox is the preferred integrated
deployment when durable local operation, appliance simplicity, and
hardware-backed controls matter. Continuity is the shared result across keys,
records, storage, events, and payments: the important things remain close
enough to use.

## What Mainstay does not become

**Mainstay is intentionally not a system of record.** It does not become the
mint, the relay, the institutional ledger, or the holder of every authority
key. It presents and coordinates state preserved by the underlying components
without claiming that the application itself is the final authority.

Working in conjunction with OpenETR, however, Mainstay can help an institution
or community preserve independently verifiable records without making the app
their source of authority. OpenETR identifies exact Digital Artifacts, preserves
signed evidence in Digital Controllable Records, and derives consequential
state under defined rules. Mainstay keeps the artifacts, evidence, and resulting
state understandable and available when conditions change. The responsible
institution, community, or relying party still decides whether to recognize
that state and what practical or legal effect to give it.

That distinction allows the app to evolve without trapping the user. Acorn
keys and proofs remain portable. Stroma keeps the Nostr wire boundary narrow
and replaceable. Grove blobs remain content-addressed. Spurline events remain
standard Nostr events. Clear currencies retain their own governance and
ledgers.

## Direction

Safebox Web is the practical application foundation. Near-term work should
continue proving each component independently, strengthen local operation, and
simplify the shared user experience before assembling the complete Lockbox
profile.

The desired result is calm capability: keys, records, payments, and local
resource coordination remain understandable when conditions change.
