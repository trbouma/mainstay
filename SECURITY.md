# Mainstay Security

## Purpose

Mainstay is a local-first control plane for a bundle of independently
addressable services, including Safebox Web, Clear, Grove, Spurline, and the
service Acorn worker. It manages deployment context, service wiring,
commissioning evidence, internal routes, operating reserves, recovery files,
and operator workflows.

A defect can expose deployment secrets, weaken a standalone service boundary,
publish an internal management path, misroute value or private data, break
recovery, or confuse operator authority with user, treasurer, or protocol
authority.

This document describes Mainstay's current security model, safeguards, trust
assumptions, and residual risks. It is intentionally candid. It is not a
certification, warranty, or claim that Mainstay is free of vulnerabilities.

## Current security status

Mainstay is pre-release software and should presently be treated as a developer
preview or hardened alpha.

- Mainstay has not received a comprehensive independent security audit.
- The service bundle, Compose topology, internal management endpoints, and
  `mainstayctl` command contracts may still change before a stable release.
- Only small test balances and non-critical records should be used.
- Security-sensitive changes should be reviewed and tested before release.
- Services managed by Mainstay must remain secure as standalone services; the
  shared Mainstay context must not become a hidden external authority.

The container interaction model is documented in
[Container Interaction and Security Model](docs/CONTAINER-INTERACTION-SECURITY-MODEL.md).
The operator utility role is documented in
[mainstayctl Operator Utility](docs/MAINSTAYCTL-OPERATOR-UTILITY.md).

## Reporting a vulnerability

Please do not disclose an unpatched vulnerability, private key, seed phrase,
Cashu proof, Clear Mint Note, token, invoice, preimage, private record,
management credential, production event data, or deployment `.env` content in a
public issue.

Use GitHub's private vulnerability-reporting feature for this repository when
it is available under **Security -> Report a vulnerability**. If that feature is
not available, open a public issue containing no sensitive or exploit details
and ask the maintainer to establish a private communication channel.

A useful report includes:

- the affected commit or version;
- the affected command, service, endpoint, Compose route, or storage path;
- minimal reproduction steps using disposable keys and test funds;
- the expected and observed result;
- the likely confidentiality, integrity, availability, recovery, or fund-safety
  impact; and
- whether the issue is already being exploited or requires urgent action.

No formal response-time service level is offered during the developer-preview
phase. Confirmed high-impact issues should block a release until they are fixed
or explicitly documented with an operational mitigation.

## What Mainstay is protecting

The principal protected assets are:

- deployment-local secrets in `.env` and generated recovery files;
- Mainstay installation identity and commissioning evidence;
- Safebox Web cookie keys, management tokens, service keys, and service Acorn
  configuration;
- Clear master or operator secrets, mint-service identity material, and
  operator paths;
- Grove, Spurline, and Safebox service identities and internal routes;
- service Acorn reserve state, funding requests, invoices, and payment status;
- local Safebox, Clear, Grove, and Spurline data volumes;
- endpoint scope information distinguishing internal, local, external, and
  future FIPS routes; and
- continuity of installation, backup, recovery, and service identity binding.

Mainstay does not make a service identity, wallet `npub`, Clear keyset ID, or
content hash depend on a specific Docker name, DNS name, or IP route. Those
routes are context. Authority must remain bound to the correct role and stable
identifier.

## Trust model

Mainstay separates local operator context from public protocol authority.
Each layer has a different security role.

| Layer | Role | What must be trusted |
| --- | --- | --- |
| Mainstay operator | Installs, configures, starts, backs up, recovers, and administers the instance | Host custody, `.env` protection, update discipline, backup handling, and correct interpretation of operator authority |
| `mainstayctl` | Root-level operator utility for shared instance context | Command implementation, management-token handling, narrow endpoint use, and avoidance of arbitrary shell or file exposure |
| Docker or local runtime | Runs the service bundle and isolates internal routes | Runtime isolation, volume permissions, network scoping, image provenance, and host firewall policy |
| Safebox Web | User-facing wallet application and internal management surface | Session security, management-token enforcement, wallet UX, and safe handling of shared request files |
| `service-acorn-worker` | Singleton owner of service Acorn wallet mutation | Wallet custody, payment checking, reserve funding, and safe worker state |
| Clear | Mint mechanics, Clear keysets, root operator and treasurer workflow | Mint database integrity, key custody, operator path isolation, treasurer authorization, and public mint correctness |
| Grove | Blob storage service | Availability, retention, content-addressed integrity, and internal/public route separation |
| Spurline | Relay service | Event acceptance, retention, indexing, availability, and route separation |
| External services | Mints, relays, DNS, Lightning, HTTPS, VPN, and future FIPS routes | Their own availability, settlement reporting, transport security, and policy behavior |

Internal Docker reachability is not by itself sufficient authorization for
privileged actions. Internal management endpoints must be narrow and protected
by deployment-local credentials. External or treasury-bearing actions must use
signed protocol authority rather than local deployment trust.

## Implemented safeguards

### Instance secrets and recovery

- `init-env.sh` generates required Mainstay and service secrets when missing.
- Recovery configuration is written separately so the operator can preserve
  identity-bound secrets outside the image.
- Mainstay refuses or warns on mismatched service data and identity assumptions
  during lifecycle operations.
- Compose configuration injects only the service variables needed by each
  container.

### Endpoint scope separation

- Registry endpoints distinguish `internal`, `local`, and `external` scopes.
- Internal Docker service names such as `http://safebox-web:8000`,
  `http://clear:3339`, and `ws://spurline:8080` are treated as instance-local
  routes.
- Public routes must be configured deliberately and must not silently replace
  internal routes when an internal dependency fails.
- Internal endpoints are diagnostics or management paths, not public discovery
  metadata.

### Internal management paths

- Safebox Web internal management endpoints use `SAFEBOX_MANAGEMENT_TOKEN`.
- Internal management tokens are opaque random bearer values, not identity
  keys. They can be rotated without changing service or treasurer `npub`s.
- Missing management credentials cause internal management endpoints to behave
  as unavailable rather than as public features.
- `mainstayctl reserve balance` and `mainstayctl reserve fund` use authenticated
  internal Safebox Web endpoints instead of requiring Docker access inside the
  admin container.
- Service Acorn reserve funding is queued through a narrow shared request file;
  the worker remains the only process mutating the service Acorn wallet.
- Reverse proxies should block `/internal/` before any catch-all proxy rule.
- Token checks are still required as an application-level backstop if an
  internal path is accidentally exposed.

### Clear operator surface

- Mainstay treats Clear root operator authority as service/operator authority,
  not currency or treasurer authority.
- Public mint paths and privileged operator paths are intended to remain
  separate.
- If Clear is exposed through a proxy, operator paths such as `/v1/operator`
  must be blocked from the public route.
- Treasury authority should be signed by authorized treasurer `npub`s rather
  than inferred from the Mainstay operator.

### Shared local context

- Shared mounts are read-only where inspection is sufficient, such as local
  Safebox handle listing from `mainstay-local`.
- Mutable wallet state stays with the owning service.
- Shared request and status files are narrow, typed, and do not contain private
  keys or recovery material.
- Diagnostic output is expected to omit private keys, recovery material, bearer
  proofs, and broad management tokens.

## Important residual risks

The current risks include:

- the code has not been independently audited;
- a host compromise can expose `.env`, data volumes, service secrets, and
  recovery files;
- Docker network privacy and file permissions are important but not complete
  security boundaries;
- a misconfigured reverse proxy can expose internal or operator endpoints if
  deployment-level blocking is not applied;
- `mainstayctl` is powerful by design and must not become an arbitrary shell,
  proxy, or broad file-access bridge;
- service images and dependency revisions are supply-chain dependencies;
- backup and recovery correctness depends on preserving matching data,
  service identities, and secrets together;
- Clear treasury workflows and stronger operator/treasurer separation are still
  evolving;
- no HSM, remote signer, or hardware-backed secret boundary is currently
  enforced by Mainstay; and
- future local, VPN, public, and FIPS routes may introduce new trust and
  correlation risks.

## Deployment guidance

- Protect the deployment directory, `.env`, recovery files, and data volumes as
  sensitive operator material.
- Publish only the routes deliberately intended for local or external clients.
- Block `/internal/` and service-specific operator paths at any reverse proxy.
- Do not publish Clear operator paths such as `/v1/operator` on a public mint
  route.
- Keep internal management credentials out of browser applications and public
  client configuration.
- Run with small test balances until the relevant services and Mainstay bundle
  have been reviewed for the intended use.
- Back up the deployment with data, secrets, and service identities from the
  same recovery point.
- Review changes that add management endpoints, shared mounts, reverse-proxy
  routes, Clear operator paths, or treasury authority.

## Security non-claims

Mainstay does not claim that:

- a standalone service becomes secure merely because Mainstay manages it;
- Docker internal networking is enough to authorize privileged actions;
- a reverse proxy is the only necessary boundary for internal paths;
- the Mainstay operator is automatically a treasurer or issuer;
- public DNS, URLs, or IP routes are durable identity;
- current deployments are audited, production hardened, or free of fund-loss
  risk.

The intended invariant is:

> Standalone services remain secure by default. Mainstay adds local operator
> context, not hidden external authority.
