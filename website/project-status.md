---
title: Project Status
description: Current state and next milestones for Mainstay.
---

# Project Status

Mainstay is currently a product vision and integration direction. This site is
the flagship reference for how the sibling products fit together.

## Available foundations

- Safebox Web provides working user-facing records and payment workflows.
- Acorn provides the portable wallet, key, record, and proof runtime.
- Grove provides working local and hosted encrypted blob storage.
- Spurline provides a tested local Nostr relay foundation.
- Clear provides an experimental non-Lightning Cashu mint for bounded local
  currencies.
- Mainstay and Lockbox product principles, continuity modes, and component
  boundaries are documented.

## Next

- continue proving each sibling component independently;
- define stable service discovery and health contracts;
- bring the current Safebox Web experience toward the Mainstay application model;
- integrate local Spurline and Grove paths;
- add Clear currency discovery without combining balances or issuers;
- define the first FreeBSD Lockbox service profile;
- design TROPIC01 and keypad authority boundaries; and
- create end-to-end local and community continuity tests.

## Repositories

- [Mainstay](https://github.com/trbouma/mainstay)
- [Safebox Web](https://github.com/trbouma/safebox-web)
- [Acorn](https://github.com/trbouma/safebox-acorn)
- [Grove](https://github.com/trbouma/grove)
- [Spurline](https://github.com/trbouma/spurline)
- [Clear](https://github.com/trbouma/clear)

!!! warning "Early-stage work"
    The product family is experimental. Do not rely on it for critical records,
    financial value, emergency operations, or production infrastructure without
    independent review and appropriate operational controls.
