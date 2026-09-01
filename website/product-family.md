---
title: Product Family
description: The sibling products Mainstay coordinates and Lockbox can run locally.
---

# Product Family

Mainstay brings together a set of independently useful products. Their clear
boundaries are a strength: each component can be deployed, tested, replaced,
and understood on its own.

<div class="product-grid" markdown>

<article class="product-card" markdown>

<a href="https://trbouma.github.io/safebox-web/" aria-label="Visit the Safebox Web website">
  <img src="../assets/safebox-logo.png" alt="Safebox Web">
</a>

## Safebox Web

The standalone user app for records, payments, recovery, handles, and everyday
wallet workflows. Safebox Web provides the practical application foundation
from which Mainstay is evolving.

[Visit Safebox Web](https://trbouma.github.io/safebox-web/)

</article>

<article class="product-card" markdown>

<a href="https://trbouma.github.io/safebox-acorn/" aria-label="Visit the Acorn website">
  <img src="../assets/acorn-logo.png" alt="Acorn">
</a>

## Acorn

The protocol-first component for user-controlled keys, funds, and records.
Acorn keeps portable signing, recovery, and wallet authority below the
application layer.

[Visit Acorn](https://trbouma.github.io/safebox-acorn/)

</article>

<article class="product-card" markdown>

<a href="https://trbouma.github.io/stroma/" aria-label="Visit the Stroma website">
  <img src="../assets/stroma-logo.png" alt="Stroma">
</a>

## Stroma

The focused Nostr wire-format library beneath Acorn. Stroma handles keys, event
encoding, signatures, NIP-44 encryption, NIP-59 gift wrapping, and bounded
relay exchange without owning application meaning.

[Visit Stroma](https://trbouma.github.io/stroma/)

</article>

<article class="product-card" markdown>

<a href="https://trbouma.github.io/grove/" aria-label="Visit the Grove website">
  <img src="../assets/grove-logo.png" alt="Grove">
</a>

## Grove

A local-first Blossom server for opaque, content-addressed encrypted blobs and
attachments. Grove preserves and retrieves bytes without needing to understand
their plaintext or application meaning.

[Visit Grove](https://trbouma.github.io/grove/)

</article>

<article class="product-card" markdown>

<a href="https://trbouma.github.io/spurline/" aria-label="Visit the Spurline website">
  <img src="../assets/spurline-logo.svg" alt="Spurline">
</a>

## Spurline

A local-first Nostr relay for durable event storage, selective synchronization,
and future community mesh operation. Spurline keeps signed events available
across connected and disrupted conditions.

[Visit Spurline](https://trbouma.github.io/spurline/)

</article>

<article class="product-card" markdown>

<a href="https://trbouma.github.io/clear/" aria-label="Visit the Clear website">
  <img src="../assets/clear-logo.svg" alt="Clear">
</a>

## Clear

The issuance, circulation and redemption machinery for organization-defined
transferable units. Clear uses private Cashu bearer notes without requiring
Bitcoin or Lightning settlement.

[Visit Clear](https://trbouma.github.io/clear/)

</article>

<article class="product-card" markdown>

<a href="https://trbouma.github.io/openetr/" aria-label="Visit the OpenETR website">
  <img src="../assets/openetr-logo.png" alt="OpenETR">
</a>

## OpenETR

The consequential-state and evidence layer for transferable records. OpenETR
preserves end-verifiable evidence of anchoring, integrity, attestation,
transfer, and termination so applications can derive consequential state.

[Visit OpenETR](https://trbouma.github.io/openetr/)

</article>

</div>

## How the pieces fit

```text
                         Mainstay
                  unified user application
                              |
             +----------------+----------------+
             |                |                |
       Safebox Web         Acorn            Clear
         user flows    portable authority   local mint
                              |
                        +-----+-----+
                        |           |
                     Stroma       Grove
                  Nostr wire      blobs
                        |
                    Spurline
                  event relay

                   Lockbox runs the stack locally

                Mainstay <----> OpenETR
                  record legitimacy
       provenance, control history, digital trade
```

Mainstay should discover available services and explain their state in plain
language. It must keep different mints, currencies, issuers, relays, and
storage providers visible enough that convenience never becomes false
equivalence.

OpenETR is not another storage provider or system of record. It complements
Mainstay with a Digital Controllable Record: end-verifiable evidence about a
record's anchoring, attestation, transfer, and termination. Mainstay can present
that evidence alongside a safeguarded record while leaving the legitimacy
judgment with the people, organizations, and authorities that recognize it.

Stroma is not another application or hosted infrastructure service. It is the
small protocol layer Acorn uses to speak Nostr without importing social-client
behavior into the wallet kernel. Spurline and other compatible relays remain
independent services on the other side of that wire boundary.

## Clear and local economies

Clear adds an optional local economic layer. A church, food-bank network,
campus, event, emergency operation, or resort can operate a bounded currency
recognized by participating people and providers.

A resort could issue guest credits, staff allowances, activity vouchers, or
emergency value on its own network. Acorn holds the proofs, Mainstay presents
the experience, Spurline carries signed local events, and Lockbox can host the
runtime. The resort treasury remains responsible for issuance and provider
settlement.

These currencies are voluntary, limited-recognition instruments rather than
legal tender. Mainstay must keep every currency and its governing organization
distinct.
