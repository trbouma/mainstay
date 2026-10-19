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
wallet workflows. Safebox Web provides Mainstay's practical application
foundation.

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

An open protocol for deriving consequential state from end-verifiable evidence
concerning exact Digital Artifacts. OpenETR keeps artifact identity, signed
evidence, derived state, and external recognition distinct.

[Visit OpenETR](https://trbouma.github.io/openetr/)

</article>

<article class="product-card" markdown>

<a href="https://trbouma.github.io/openqr/" aria-label="Visit the OpenQR website">
  <img src="../assets/openqr-logo.svg" alt="OpenQR">
</a>

## OpenQR

The public acquisition and presentation surface for OpenETR evidence. OpenQR
turns a printed QR code or digital link into a digest-verified artifact and its
signed Anchor Records, while leaving authenticity, authority, and recognition
to the applicable rulebook.

[Visit OpenQR](https://trbouma.github.io/openqr/)

</article>

<article class="product-card" markdown>

<a href="https://trbouma.github.io/oakgate/" aria-label="Visit the OakGate website">
  <img src="../assets/oakgate-logo.png" alt="OakGate">
</a>

## OakGate

A managed entrance to Acorn-backed safeboxes. OakGate provides familiar
Keycloak sign-in today and is building the custodial storage, recovery, and
Go Independent path needed to let a person later assume direct responsibility
for the same safebox.

[Visit OakGate](https://trbouma.github.io/oakgate/)

</article>

</div>

## How the pieces fit

```text
                         Mainstay
                  unified user application
                              |
             +----------------+----------------+
             |                |                |
       Safebox Web         OakGate           Clear
       direct access    managed access      local mint
             |                |                |
             +------------ Acorn -------------+
                       portable authority
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
             evidence and derived state
                              |
                           OpenQR
                  scan, resolve, and inspect
```

Mainstay discovers available services and explains their state in plain
language. It must keep different mints, currencies, issuers, relays, and
storage providers visible enough that convenience never becomes false
equivalence.

Across the family, the public proposition is **Move Value. Check Status.**
Clear, Acorn, and the safebox applications support the movement of
community-defined value. OpenETR and OpenQR support checking the consequential
state of records and claims. Mainstay coordinates the experience while leaving
issuance, settlement, verification, and recognition with the components and
governing parties responsible for them.

Value can be monetary, contractual, institutional, or embodied in physical
goods. The family can record and verify changes in control, custody, shipment,
delivery, and acceptance, but the evidence of a transition is not the physical
transition itself and does not independently determine legal ownership.

OpenETR is not another storage provider or system of record. It complements
Mainstay with Digital Controllable Records: portable signed evidence from which
consequential state can be derived under defined rules. Mainstay can present an
exact Digital Artifact, its evidence, and the resulting state while leaving
recognition and effect with the people, organizations, and authorities relying
on it.

OpenQR makes that evidence approachable at the point of use. It resolves a QR
or GS1 Digital Link, verifies exact artifact bytes and signed anchors, and
presents the result for inspection. It does not decide whether an issuer is
authorized, a product is authentic, or a record has legal or community effect.

OakGate and Safebox Web offer different access and custody choices around
Acorn. Safebox Web does not retain a user's signing key. OakGate deliberately
takes on a managed relationship: its sign-in foundation works today, while
Acorn integration, custodial recovery, and the Go Independent exit process are
still under construction. Those responsibilities must be explicit rather than
blurred into a generic login experience.

Stroma is not another application or hosted infrastructure service. It is the
small protocol layer Acorn uses to speak Nostr without importing social-client
behavior into the wallet kernel. Spurline and other compatible relays remain
independent services on the other side of that wire boundary.

## Clear and local economies

Clear adds an optional local economic layer. A church, food-bank network,
campus, event, resort, co-working facility, or Indigenous community program can
operate bounded credits recognized by participating people and providers.

A resort could issue guest credits, staff allowances, activity vouchers, meal
credits, or local service credits on its own network. Acorn holds the proofs,
Mainstay presents the experience, Spurline carries signed local events, and
Lockbox can host the runtime. The resort treasury remains responsible for
issuance and provider settlement.

These currencies are voluntary, limited-recognition instruments rather than
legal tender. Mainstay must keep every currency and its governing organization
distinct.
