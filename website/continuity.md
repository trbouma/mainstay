---
title: Continuity
description: How Mainstay keeps records and payments understandable across changing conditions.
---

# Continuity

## When distant infrastructure disappears

A satellite link goes down. A distant cloud service starts behaving
unpredictably. A tornado takes out the local registry office and bank. Solar
power and backup systems are keeping the electricity on, but the community has
lost access to much of what it needs to function: payment services, critical
records, local evidence, and the remote systems used to coordinate them.

The people, funds, and records have not disappeared. The paths used to reach
them have. Mainstay is intended to provide a local point of continuity: keeping
nearby records and payment capabilities understandable and usable, supporting
community coordination, and reconciling with external systems when
connectivity returns.

Continuity means that records, identity, and value remain usable when external
conditions change. It does not mean pretending every action has the same level
of finality.

## Four operating modes

| Mode | Meaning |
| --- | --- |
| **Connected Mode** | Hosted services, public relays, external mints, synchronization, and updates are available. |
| **Local Mode** | The user reaches nearby Lockbox services directly without depending on upstream internet. |
| **Mobile Mode** | A phone or nearby device supplies temporary upstream connectivity while local services remain primary. |
| **Community Mode** | Participating devices and Lockboxes exchange signed events, encrypted records, and value across a local network or mesh. |

The same user app should work across all four. A mode change should alter
availability and finality messaging, not force people into an unfamiliar
emergency interface.

## Good boundaries, not barriers

Continuity requires clear boundaries because different components fail in
different ways and answer to different authorities. A relay can preserve an
event but cannot declare an ecash proof spendable. Mainstay can preserve and
present a record but does not become its institutional authority. A local
service can keep operating without pretending that an unavailable external
service has confirmed anything.

These boundaries contain failures, preserve honest status, and make each
component independently replaceable. They must not become barriers. Open
protocols allow signed events, encrypted records, proofs, and control evidence
to move or synchronize across compatible local and remote infrastructure.
Continuity comes from maintaining those connections without erasing the
meaning of the boundaries they cross.

## Records and evidence

Spurline preserves relevant Nostr events locally. Grove preserves encrypted
blobs. Acorn retains portable keys, records, and recovery material. When a
network path returns, local activity can synchronize outward without losing
its original signatures or evidence trail.

## Two payment continuity paths

Mainstay must distinguish two different situations.

### External mint unavailable

Acorns can transfer previously issued ecash locally when an external Cashu
mint or Lightning path is unreachable. The receiver preserves the proofs as
pending until the mint can confirm, refresh, or reject them.

```text
Local transfer accepted
Mint finality pending
Reconciliation required when connected
```

If exact change cannot be made without the mint, the app should show the
closest available amounts and ask for explicit approval.

### Local Clear mint available

A Clear mint on the local network can validate, swap, issue, and retire its own
currency without Bitcoin, Lightning, or global internet access. That provides
mint-level finality for that bounded currency while the local mint remains
reachable.

This is useful for resorts, ships, campuses, remote communities, food-bank
networks, and emergency operations that retain a local network during an
upstream outage.

## Honest status is a feature

Mainstay should make three signals obvious:

- **confirmed** value has finality from the relevant mint;
- **pending** value is preserved but still needs finalization; and
- **local availability** explains which services can currently be reached.

The product promise is not uninterrupted access to every external dependency.
It is continuity without ambiguity.
