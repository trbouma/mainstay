# mainstayctl Operator Utility

`mainstayctl` is the root-level operator utility for a Mainstay instance. It is
the fast local tool an operator uses when a management action belongs to the
whole instance rather than to one public protocol surface or one user's wallet.

The command exists because a Mainstay instance has shared local context that no
single application container should pretend to own alone. Safebox Web, Clear,
Grove, Spurline, the service Acorn worker, and future services each keep their
own identities and responsibilities. `mainstayctl` provides the operator with a
controlled way to coordinate them inside one deployment boundary.

## Role

`mainstayctl` is not a user wallet, public API, reverse proxy, or treasurer
authority. It is an operator tool for the person or automation responsible for
the instance.

Its job is to:

- read deployment-local context quickly;
- call narrow internal management endpoints;
- assemble commands that require knowledge of several containers;
- inspect service status, reserve state, handles, and commissioning evidence;
- perform operator maintenance without exposing Docker or root shell access to
  application users;
- preserve separation between local operator convenience and external protocol
  authority.

This makes it closer to a system administration utility than an application
feature. The rename from the older `mainstay-local` entry point to
`mainstayctl` reflects that role.

## Shared Root Context

Within one Mainstay instance, several containers share a root or local context:

- the instance `.env`;
- Docker Compose service names and private network routes;
- shared volumes such as Safebox data;
- operator-generated service secrets;
- internal-only management credentials;
- local evidence about commissioned services and endpoint scopes.

`mainstayctl` is allowed to use that context because it is run by the instance
operator. For example, it may read a local Safebox handle database through a
read-only mount, call Safebox Web over `http://safebox-web:8000/internal/...`,
or ask the service Acorn worker to fund an operating reserve.

The important boundary is that this shared context is local to the deployment.
It must not be treated as an external protocol or published as public metadata.

## Why Not Put Everything in One Container?

Each service still owns its own domain:

- Safebox Web owns the user-facing wallet application and local wallet UX;
- `service-acorn-worker` owns mutable service Acorn wallet operations;
- Clear owns mint mechanics and Clear operator surfaces;
- Spurline owns relay behavior;
- Grove owns blob storage behavior;
- Mainstay owns orchestration, context, installation lifecycle, and recovery.

`mainstayctl` coordinates these services without collapsing them into one
monolithic process. When an action requires wallet mutation, the command should
ask the wallet-owning process to do the work. When an action requires local
database context, it should read the minimum necessary state. When an action is
external or treasury-related, it should use the signed protocol authority for
that role.

## Current Command Families

### Instance and Service Lifecycle

These commands operate the bundle and inspect its services:

```text
mainstayctl init
mainstayctl config
mainstayctl status
mainstayctl up
mainstayctl service commission clear
mainstayctl service show clear
mainstayctl service verify clear
```

They belong to `mainstayctl` because they require Mainstay instance context:
the registry, Compose configuration, service identities, and commissioning
evidence.

### Local Clear Operations

```text
mainstayctl clear send <amount> <local-handle>
```

This is an operator convenience command for same-instance Clear distribution.
It resolves a bare local handle using the local Safebox context, uses internal
Clear and Spurline routes, and avoids asking the operator to manually assemble
Docker-network addresses.

It is not a general external Clear send command. External Clear behavior must
respect recipient advertisement, public mint reachability, relay reachability,
and signed protocol rules.

### Service Acorn Reserve

```text
mainstayctl reserve balance
mainstayctl reserve fund <amount>
```

These commands inspect and fund the service Acorn operating reserve. The
container-native path uses Safebox Web's authenticated internal management
endpoint. Safebox Web then communicates with `service-acorn-worker` through
shared local request state so that the worker remains the only process mutating
the service Acorn wallet.

This keeps the operator flow quick while preserving service ownership.

### Local Directory and Diagnostic Commands

```text
mainstayctl handles
```

Commands like this are instance-local diagnostics. They use read-only access to
deployment state to answer practical operator questions, such as which handles
are registered and where their home relay points.

## Security Boundaries

`mainstayctl` should follow these rules:

1. Treat root/operator context as local to one instance.
2. Prefer read-only shared mounts for inspection.
3. Use authenticated internal management endpoints for live service operations.
4. Avoid Docker access inside the admin container when a narrow management
   endpoint can do the job.
5. Do not expose `/internal/` management paths through a public reverse proxy.
6. Do not export private keys, recovery material, bearer proofs, or management
   tokens in command output.
7. Keep wallet mutation with the service that owns the wallet.
8. Require signed protocol envelopes for remote treasury functions.
9. Keep root operator authority separate from currency or treasurer authority.
10. Fail closed when an internal-only route is unavailable.

The tool is powerful because the operator is powerful. The code should make
that power explicit, narrow, and auditable.

## Relationship to Treasurer Authority

`mainstayctl` may perform root operator functions for the instance: start
services, inspect health, commission managed services, test local mint
reliability, and fund operating reserves.

It does not make the Mainstay operator the treasurer of every currency. A
treasurer controls issuance policy, liability, redemption expectations, and
currency-specific authorization. Remote treasury commands should be authorized
by signed envelopes from the appropriate treasurer `npub`.

This separation is essential for future portability. A treasurer may eventually
move circulation state from one mint operator to another. That should not
depend on giving the old or new operator currency authority.

## Design Direction

As Mainstay evolves, `mainstayctl` should remain the place for:

- instance setup and recovery;
- service commissioning and verification;
- shared-context diagnostics;
- internal management requests;
- backup and continuity coordination;
- operator reserve and reliability checks;
- migration from Docker Compose to other local-first runtimes.

It should not become:

- a public API;
- an arbitrary shell bridge;
- a replacement for signed external protocols;
- a hidden wallet owner;
- a catch-all escape hatch around service boundaries.

The useful pattern is:

```text
operator intent
  -> mainstayctl
  -> shared local context or authenticated internal endpoint
  -> owning service performs the narrow operation
  -> safe status returns to the operator
```

That is the model that lets management functions happen quickly while keeping
Mainstay's authority boundaries legible.
