---
title: Product Vision
description: The product promise, principles, and direction for Mainstay.
---

# Product Vision

**Mainstay is a local-first application for keys, records, payments, and
community resource coordination that keeps working across connected and
disrupted conditions.**

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

## The product model

```text
Mainstay is the application.
Lockbox is the appliance.
Continuity is the capability.
```

Mainstay is the primary user entry point. Lockbox is the preferred integrated
deployment when durable local operation, appliance simplicity, and
hardware-backed controls matter. Continuity is the shared capability across
keys, records, storage, events, and payments.

## What Mainstay does not become

**Mainstay is intentionally not a system of record.** It does not become the
mint, the relay, the institutional ledger, or the holder of every authority
key. It presents and coordinates state preserved by the underlying components
without claiming that the application itself is the final authority.

Working in conjunction with OpenETR, however, Mainstay can support a system of
record that needs continuity of its records. OpenETR contributes signed
evidence about origin, attestation, integrity, transfer, and termination;
Mainstay keeps that evidence and its associated records understandable and
available across connected and disrupted conditions. The responsible
institution, community, or recognized authority still determines what is
legitimate and authoritative.

That distinction allows the app to evolve without trapping the user. Acorn
keys and proofs remain portable. Grove blobs remain content-addressed.
Spurline events remain standard Nostr events. Clear currencies retain their
own governance and ledgers.

## Direction

Safebox Web is the practical application foundation. Near-term work should
continue proving each component independently, strengthen local operation, and
simplify the shared user experience before assembling the complete Lockbox
profile.

The desired result is calm capability: keys, records, payments, and local
resource coordination remain understandable when conditions change.
