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

<img src="assets/safebox-logo.png" alt="Safebox">

## Safebox

The current standalone user app for records, payments, recovery, handles, and
everyday wallet workflows. It is the practical application foundation for
Mainstay.

[Website](https://getsafebox.app) · [Source](https://github.com/trbouma/safebox-web)

</article>

<article class="product-card" markdown>

<img src="assets/acorn-logo.png" alt="Acorn">

## Acorn

The wallet, identity, signing, record, proof, and recovery runtime. Acorn keeps
portable protocol authority below the application layer.

[Website](https://trbouma.github.io/safebox-acorn/) · [Source](https://github.com/trbouma/safebox-acorn)

</article>

<article class="product-card" markdown>

<img src="assets/grove-logo.png" alt="Grove">

## Grove

A local-first Blossom server for opaque, content-addressed encrypted blobs and
attachments. Grove preserves bytes without needing to understand plaintext.

[Website](https://trbouma.github.io/grove/) · [Source](https://github.com/trbouma/grove)

</article>

<article class="product-card" markdown>

<img src="assets/spurline-logo.svg" alt="Spurline">

## Spurline

A local-first Nostr relay for event continuity, selective synchronization, and
future community mesh operation.

[Website](https://trbouma.github.io/spurline/) · [Source](https://github.com/trbouma/spurline)

</article>

<article class="product-card" markdown>

<img src="assets/clear-logo.svg" alt="Clear">

## Clear

An optional local-first Cashu mint for independently governed points, vouchers,
and internal economies without Bitcoin or Lightning settlement.

[Website](https://trbouma.github.io/clear/) · [Source](https://github.com/trbouma/clear)

</article>

<article class="product-card product-card--mainstay" markdown>

<img src="assets/mainstay-logo.svg" alt="Mainstay">

## Mainstay

The unified application and primary user entry point. Mainstay coordinates the
family without replacing their protocol boundaries.

[Source](https://github.com/trbouma/mainstay)

</article>

</div>

## How the pieces fit

```text
                         Mainstay
                  unified user application
                              |
             +----------------+----------------+
             |                |                |
          Safebox           Acorn            Clear
         user flows    portable authority   local mint
                              |
                        +-----+-----+
                        |           |
                    Spurline      Grove
                     events       blobs

                   Lockbox runs the stack locally
```

Mainstay should discover available services and explain their state in plain
language. It must keep different mints, currencies, issuers, relays, and
storage providers visible enough that convenience never becomes false
equivalence.

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
