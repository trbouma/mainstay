---
title: Lockbox Appliance
description: The hardware-first local appliance direction for Mainstay and its supporting services.
---

# Lockbox Appliance

**Mainstay is the application. Lockbox is the appliance.**

Lockbox is the hardware-first deployment that gives Mainstay and its supporting
services a dedicated local home. It is intended for people and communities
that need durable storage, predictable service operation, local networking,
and hardware-backed controls.

<img class="lockbox-hero-image" src="assets/lockbox-appliance-concept.jpg" alt="Lockbox appliance with a phone on a table">

## Initial platform direction

```text
FreeBSD on Raspberry Pi 4
with a physical keypad and TROPIC01 HSM
```

- **FreeBSD** provides a small, inspectable, service-oriented base.
- **Raspberry Pi 4** supplies a low-power initial hardware target.
- **TROPIC01** provides a future hardware-backed key and signing boundary.
- **The keypad** supplies local presence for unlock, approval, and recovery.

## Appliance profile

A Lockbox deployment can run:

- Mainstay as the unified user application;
- Safebox as the current application foundation;
- Acorn for keys, records, proofs, signing, and recovery;
- Spurline for local Nostr event continuity;
- Grove for encrypted blob storage; and
- optionally, Clear for a locally governed currency or voucher system.

Not every Lockbox needs every component. Clear in particular must be an
explicit organizational choice: operating an appliance must never silently
make someone a currency issuer.

## Local authority

> Network services can assist. Local presence controls authority.

Remote services may improve availability, but high-risk local actions should
eventually be constrained by hardware-backed policy and physical approval. The
web app can request an operation; the local boundary decides whether it may
proceed.

## Appliance, not general-purpose server

Lockbox should boot predictably, expose clear health information, use stable
local service addresses, keep data in documented locations, and support safe
backup, migration, restart, and shutdown behavior.

The first goal is a coherent local profile for the existing sibling products,
not a generic home-server platform or a monolithic rewrite.
