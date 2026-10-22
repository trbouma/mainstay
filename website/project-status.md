---
title: Project Status
description: What works today and what remains under construction in Mainstay.
---

# Project Status

Mainstay is a working, early-stage local-first product. Its installer brings up
an integrated service bundle and dashboard, while this site documents how the
sibling products fit together and which parts are still under construction.

## Available today

- Safebox Web provides working user-facing records and payment workflows.
- Acorn provides the portable wallet, key, record, and proof runtime.
- Stroma provides an initial tested Nostr wire-format library for Acorn's
  incremental migration away from a general social-client dependency.
- Grove provides working local and hosted encrypted blob storage.
- Spurline provides a tested local Nostr relay foundation.
- Clear provides an experimental non-Lightning Cashu mint for bounded local
  currencies.
- OpenQR provides a working public resolver, artifact checker, and registration
  surface for OpenETR anchors, with optional verified artifact retrieval.
- OakGate provides a working FastAPI and Keycloak sign-in foundation for a
  managed safebox experience.
- Mainstay provides an interactive installer, recovery workflow, service-health
  dashboard, and integrated Docker Compose deployment.
- Mainstay and Lockbox product principles, continuity modes, and component
  boundaries are documented.

## Under construction

- continue proving each sibling component independently;
- define stable service discovery and health contracts;
- bring the current Safebox Web experience toward the Mainstay application model;
- integrate local Spurline and Grove paths;
- add Clear currency discovery without combining balances or issuers;
- complete OakGate's Acorn integration, custodial recovery, and Go Independent
  workflow;
- integrate OakGate, private Redis sessions, and durable Keycloak identity as
  an optional Mainstay deployment profile before considering OakGate the
  default managed web client, following the
  [deployment integration review](https://github.com/trbouma/mainstay/blob/main/docs/OAKGATE-MAINSTAY-DEPLOYMENT-INTEGRATION.md);
- define the first FreeBSD Lockbox service profile;
- design TROPIC01 and keypad authority boundaries; and
- create end-to-end local and community continuity tests.

## Repositories

- [Mainstay](https://github.com/trbouma/mainstay)
- [Safebox Web](https://github.com/trbouma/safebox-web)
- [Acorn](https://github.com/trbouma/safebox-acorn)
- [Stroma](https://github.com/trbouma/stroma)
- [Grove](https://github.com/trbouma/grove)
- [Spurline](https://github.com/trbouma/spurline)
- [Clear](https://github.com/trbouma/clear)
- [OpenETR](https://github.com/trbouma/openetr)
- [OpenQR](https://github.com/trbouma/openqr)
- [OakGate](https://github.com/trbouma/oakgate)

!!! warning "Early-stage work"
    The product family is experimental. Do not rely on it for critical records,
    financial value, emergency operations, or production infrastructure without
    independent review and appropriate operational controls.
