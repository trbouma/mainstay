---
title: Lockbox Appliance
description: The hardware-first local appliance direction for Mainstay and its supporting services.
---

# Lockbox Appliance

**Mainstay is the application. Lockbox is the appliance.**

Lockbox is the hardware platform for supporting a locally running Mainstay
instance and its services. It gives that deployment a dedicated local home and
serves people and communities that need durable storage, predictable service
operation, local networking, and hardware-backed controls.

<img class="lockbox-hero-image" src="../assets/lockbox-appliance-concept.jpg" alt="Lockbox appliance with a phone on a table">

## Initial platform direction

```text
FreeBSD on Raspberry Pi 4
with a physical keypad and TROPIC01 HSM
```

- **FreeBSD** provides a small, inspectable, service-oriented base.
- **Raspberry Pi 4** supplies a low-power initial hardware target.
- **TROPIC01** is the planned hardware-backed key and signing boundary.
- **The keypad** supplies local presence for unlock, approval, and recovery.

## Appliance profile

A Lockbox deployment can run:

- Mainstay as the unified user application;
- Safebox Web as the current application foundation;
- Acorn for keys, records, proofs, signing, and recovery;
- Stroma as Acorn's narrow Nostr wire-format library;
- Spurline for local Nostr event continuity;
- Grove for encrypted blob storage; and
- optionally, Clear for a locally governed currency or voucher system.

Not every Lockbox needs every component. Clear in particular must be an
explicit organizational choice: operating an appliance must never silently
make someone a currency issuer.

Stroma is packaged with the software that uses it rather than operated as a
separate appliance service. It keeps Acorn's Nostr protocol dependency small
and inspectable while Spurline remains an independently replaceable relay.

## Local Approval

> Network services can assist. Sensitive actions stay locally approved.

Remote services may improve availability. The planned hardware-backed policy
and physical-approval boundary constrains high-risk local actions: the web app
can request an operation, while the local boundary decides whether it may
proceed.

## Appliance, not general-purpose server

The Lockbox appliance profile specifies predictable boot, clear health
information, stable local service addresses, documented data locations, and
safe backup, migration, restart, and shutdown behavior.

The first goal is a coherent local profile for the existing sibling products,
not a generic home-server platform or a monolithic rewrite.
