# Mainstay Privacy Model

Status: design and deployment guidance  
Assessment context: PIPEDA fair information principles  
Date: 2026-09-18

## Purpose

Mainstay is a local-first operating context for independently useful products.
It can bring Safebox Web, Clear, Grove, Spurline, and related workers into one
locally operated instance while interoperating with external services and with
OpenETR evidence.

This note explains the resulting privacy architecture:

- what each component can observe;
- which party is responsible for each information-handling decision;
- what normally remains inside a Mainstay instance;
- what may leave the instance;
- what encryption does and does not conceal;
- what deletion can and cannot accomplish; and
- what an operator must decide and disclose before serving real people.

The note is informed by the Office of the Privacy Commissioner of Canada's
[PIPEDA Self-Assessment Tool](https://www.priv.gc.ca/en/privacy-topics/privacy-laws-in-canada/the-personal-information-protection-and-electronic-documents-act-pipeda/pipeda-compliance-help/pipeda-compliance-and-training-tools/pipeda_sa_tool_200807/).
It is an architecture and deployment document, not a legal opinion or a claim
that software by itself is compliant with PIPEDA or another privacy law.

## Central Principle

> Privacy responsibility follows custody, visibility, authority, and purpose.
> Running components locally reduces exposure, but it does not remove the
> operator's responsibility for the personal information the deployment handles.

Mainstay does not turn all information into one central dataset. It coordinates
services while preserving their boundaries. An organization operating a
Mainstay instance may nevertheless control personal information across several
of those services. Encryption may prevent an infrastructure component from
reading content while still allowing it to observe identifiers, timing, size,
network addresses, access patterns, or relationships.

Local-first therefore means that a deployment can keep important capability and
custody close to the people it serves. It does not mean local-only, anonymous,
automatically lawful, or exempt from accountable governance.

## Privacy Roles

Technical names do not determine legal roles. Before deployment, the parties
must identify who decides why and how personal information is handled.

### Instance operator

The instance operator installs, configures, administers, backs up, restores,
monitors, and eventually retires the Mainstay instance. Depending on the
deployment, this may be an individual, a community organization, a business, a
public institution, or a service provider acting for another organization.

The operator normally controls:

- enabled services and public routes;
- local data volumes, logs, backups, and recovery files;
- external relay, Grove, mint, Lightning, DNS, proxy, and hosting choices;
- retention and deletion settings within its control;
- administrative access and incident response; and
- the notices, support, access, correction, and complaint channels offered to
  people using the instance.

The operator is not automatically the owner of a person's Acorn keys, records,
or funds. Operational power over a host also must not be presented as legal
authority over the people or records served by that host.

### Experience or program owner

A white-labelled experience, community program, employer, issuer, or public
service may determine why information is requested and which workflows are
offered. That organization may remain accountable even when another party runs
the Mainstay host. Branding does not conceal or transfer this responsibility.

### Independent service operators

An external relay, Grove provider, mint, Lightning provider, DNS provider,
reverse proxy, hosting provider, or OpenETR participant may operate under its
own authority and policy. The Mainstay operator must determine whether that
party processes information on its behalf or acts independently. A URL or
service `npub` identifies a route or technical role; it does not answer this
governance question.

### Member or user

A person may control an Acorn key, authorize a payment, maintain private
records, or decide to present information. User control is an important product
property, but it does not eliminate information visible to the application,
infrastructure operators, counterparties, or public networks.

## Component Observation and Responsibility Map

| Component | Primary role | Information it may observe or hold | Privacy boundary |
| --- | --- | --- | --- |
| Mainstay | Deployment lifecycle, local context, service wiring, recovery, and operator coordination | Installation identity, enabled services, scoped endpoints, health, configuration, deployment secrets, recovery material, local volume and backup context | Mainstay should coordinate privacy-relevant settings and evidence without becoming a general reader of user records or wallet state. |
| Safebox Web | Human-facing workflows for Acorn keys, records, funds, sharing, and presentation | Encrypted session contents while in use, wallet public key, selected relay and mint, requested records, transaction inputs and results, claimed handles, provider-payment jobs, errors, and request metadata | Safebox Web must request only the state needed for the current workflow, explain consequential disclosures, and avoid treating an encrypted browser session as invisibility from the application process. |
| Acorn | Portable key, wallet, proof, record, recovery, and protocol authority embedded in Safebox Web or another application | Plaintext keys, proofs, records, and recovery data while operating; encrypted relay state; configured endpoints; protocol results | Acorn owns portable cryptographic operations and minimizes application coupling. Its caller remains responsible for presentation, deployment, logging, consent, and lawful purpose. |
| Clear | Mint mechanics, keysets, proof state, supply accounting, and operator or treasurer workflows | Mint requests, proof state, keyset and unit information, timing, network metadata, and operator records; possibly policy-linked transaction context | Clear validates and accounts for transferable units. It must not infer a person's acceptance, identity, or legal entitlement merely from possession of a proof or access to a route. |
| Grove | Opaque, content-addressed blob storage and retrieval | Ciphertext, content hash, size, upload and retrieval time, authorization material, network address, and access patterns | Encryption can hide attachment content from Grove, but not storage and traffic metadata. Grove policy determines availability, retention, physical deletion, logs, and backups. |
| Spurline | Nostr event acceptance, retention, indexing, query, and delivery | Event envelopes, kinds, public authors where exposed, timestamps, sizes, subscriptions, network addresses, replication relationships, and encrypted payloads | Encrypted content does not conceal all event or traffic metadata. Spurline acceptance is not proof of purpose, consent, accuracy, recognition, or recipient acceptance. |
| OpenETR | Signed evidence for exact Digital Artifacts and derived record state | Artifact digests, signed Anchor and control evidence, issuer or controller identifiers, event history, and public or restricted evidence selected by participants | A digest and evidence graph can be personal information or enable correlation. Verifiability must not be confused with permission to publish or disclose. OpenETR is adjacent to, not automatically part of, every Mainstay runtime. |
| Reverse proxy and network operator | TLS termination, routing, filtering, and network operation | Domains, client and upstream addresses, timing, paths and headers, encrypted session cookies, traffic volume, and possibly plaintext HTTP at the termination point | The proxy is part of the trusted execution path. An allowlist for forwarded headers does not prevent an authorized proxy from observing or altering traffic. |
| External mint, relay, blob, Lightning, Bitcoin, DNS, rate, or hosting service | Service-specific external dependency | The identifiers, requests, amounts, lookups, routes, timing, and other metadata required by its protocol | Each external call crosses the instance boundary. The operator must assess the provider, location, terms, retention, safeguards, and foreseeable correlation. |

## Information Flow Model

Mainstay uses the three context lanes defined by the
[Container Interaction and Security Model](CONTAINER-INTERACTION-SECURITY-MODEL.md).
Each has a different privacy posture.

### Shared local context

Shared local context stays within one instance through volumes, files,
environment variables, and narrow request or status artifacts.

Typical information includes:

- service configuration and scoped routes;
- the Safebox claimed-handle database exposed read-only to an authorized local
  surface;
- service-Acorn request and status files;
- service data volumes;
- `.env` secrets and recovery files; and
- backup and restoration manifests.

Local storage reduces disclosure to remote providers but concentrates custody
in the host and its backups. The operator, host administrator, malware running
with sufficient authority, and anyone obtaining an unprotected backup may be
able to reach this information. Local context must therefore be minimized,
permission-protected, backed up deliberately, and included in retention and
incident-response planning.

### Internal management context

Internal HTTP endpoints support narrow operator actions inside the private
runtime network. They use deployment-local management credentials and must not
become general-purpose data or command bridges.

Management responses should contain the smallest operational result needed for
the task. Private keys, recovery phrases, bearer proofs, record contents, broad
tokens, and unrelated user information must not appear in health, status, or
inventory responses.

### External protocol context

Information leaves the instance when a workflow uses an external endpoint or
publishes portable protocol evidence. Examples include:

- publishing or querying Nostr events through a relay;
- uploading or retrieving ciphertext through Grove or another blob service;
- interacting with a Clear or Cashu mint;
- creating or paying a Lightning invoice;
- resolving a public NIP-05 handle through DNS and HTTPS;
- querying a Bitcoin backend;
- fetching an external currency rate;
- presenting a record or QR descriptor to another party; and
- publishing or retrieving OpenETR evidence.

The operator must not describe these flows as remaining local merely because
Mainstay selected the route or encrypted the payload.

## Representative Flows

### Private record with an attachment

```text
person
  -> Safebox Web handles plaintext for the requested operation
  -> Acorn encrypts record metadata and attachment content
  -> Spurline stores the encrypted record event and visible event metadata
  -> Grove stores attachment ciphertext and visible storage metadata
  -> the person's Acorn retains the authority needed to decrypt
```

The ordinary design keeps plaintext away from Spurline and Grove. Safebox Web
and Acorn still process plaintext and keys in memory. The relay and blob
operator can observe different metadata, and a network observer or common
operator may correlate the flows.

### Claimed handle and incoming payment

```text
person chooses a public handle
  -> Safebox Web stores handle, wallet npub, and relay information
  -> DNS/HTTPS makes the mapping publicly resolvable
  -> payer or Lightning provider submits payment-related information
  -> service Acorn and provider jobs settle and deliver encrypted value
  -> recipient Acorn receives the transfer through its relay
```

A handle is intentionally public, but its association with a wallet key,
relay, invoices, amounts, timing, comments, and delivery results can still be
personal and sensitive. Publishing a handle does not imply consent to unrelated
profiling, marketing, or indefinite retention of payment records.

### Clear transfer

```text
sender Acorn exports exact Clear proofs
  -> Spurline carries an encrypted transfer to the recipient
  -> recipient reviews and accepts or deletes the pending transfer
  -> recipient Acorn asks the identified Clear mint to verify and refresh
  -> confirmed proof state and history return to encrypted wallet records
```

The relay need not read the token, but it may observe delivery metadata. The
mint observes proof operations. The recipient's explicit acceptance is distinct
from relay delivery, technical validity, organizational recognition, and any
legal or program entitlement represented by the transferable unit.

### OpenETR evidence

```text
exact Digital Artifact
  -> digest identifies the exact bytes
  -> signed Anchor and control events record claims and changes
  -> a verifier checks evidence and applies its own recognition policy
```

The artifact need not be published for its digest and evidence to be useful.
Nevertheless, a digest can permit confirmation or correlation when another
party already has a candidate artifact. Evidence should include only the public
or audience-appropriate facts required for its purpose.

## Privacy Invariants

All Mainstay profiles and integrations should preserve these invariants.

1. **No hidden central record store.** Mainstay does not copy wallet records,
   proofs, or attachments into a general control-plane database.
2. **Purpose precedes movement.** A component sends information across a local,
   internal, or external boundary only for a documented workflow purpose.
3. **Minimum necessary context.** Each component receives only the fields and
   resource scope required for its responsibility.
4. **Encryption claims stay precise.** Documentation distinguishes plaintext
   confidentiality from metadata visibility, operator access, endpoint
   correlation, retention, integrity, and availability.
5. **Identity is not consent.** A key, signature, public handle, token, or
   possession proof does not establish permission for an unrelated use.
6. **Reachability is not authority.** A reachable endpoint does not establish
   operator authority, recognition, acceptance, or lawful disclosure.
7. **Operator access stays narrow.** Management credentials and local root
   access are not repurposed as protocol authority or routine access to user
   content.
8. **Public facts remain purpose-bound.** Public keys, handles, digests, events,
   and service records may still be personal information and must not be reused
   merely because they are technically public.
9. **Deletion is described honestly.** The interface distinguishes local
   removal, cryptographic unavailability, protocol deletion requests, provider
   deletion, backup expiry, and verified physical erasure.
10. **Deployment choices are visible.** People can learn which organization
    operates the experience, which services are local or external, and where to
    ask questions, request access or correction, or raise a concern.
11. **Logs are disclosure surfaces.** Secrets, plaintext records, proofs,
    recovery material, tokens, full invoices, and unnecessarily identifying
    errors do not enter routine logs.
12. **New purposes trigger review.** A new integration, public field,
    replication target, analytics feature, AI use, or secondary use requires a
    privacy review before activation.

## Consent and User Decisions

Safebox Web should obtain an explicit user decision at the point of a
consequential action, including sharing or presenting a record, publishing a
handle, sending value, enabling a persistent recovery convenience, or
disclosing information to a new external service.

The decision screen should state, in plain language:

- what information will be used or disclosed;
- the immediate purpose;
- the recipient or category of service;
- whether the information or metadata leaves the Mainstay instance;
- whether the action creates a public or durable record;
- what the person can later stop, withdraw, correct, or delete; and
- any consequence of declining or withdrawing.

A transaction confirmation is not blanket consent to all system processing.
Essential processing should be separated from optional publication, analytics,
research, marketing, model training, or other secondary purposes. Mainstay
must not provide a deployment-wide switch that silently converts an existing
local purpose into a new external use.

## Retention and Deletion

Mainstay coordinates components with different storage semantics. One generic
`delete` claim would be misleading.

| Layer | What deletion may mean | Limitation to disclose |
| --- | --- | --- |
| Safebox session | Expire or clear the encrypted browser cookie | This disconnects the browser; it does not delete relay events, blobs, mint state, public handles, logs, or backups. |
| Acorn record | Publish an authored deletion request and remove or supersede wallet metadata | Relays and mirrors may retain earlier ciphertext or ignore deletion requests. |
| Temporary sharing or presentation | Delete or make unavailable the temporary encrypted transfer copy | A recipient may already have viewed, copied, photographed, or independently retained the information. |
| Grove blob | Request deletion of the stored ciphertext | Provider replicas, logs, caches, or backups may persist according to policy; a content hash may remain in records or evidence. |
| Spurline event | Apply the relay's event expiry or deletion policy | Nostr deletion is advisory outside the operator's controlled relay set. Other relays or recipients may retain events. |
| Clear or Cashu proof state | Spend, refresh, retire, or record proof state | Financial, mint, fraud, security, or accounting records may have distinct retention duties and cannot be described as ordinary record deletion. |
| Safebox provider database | Delete or anonymize handles, payment jobs, comments, errors, and coordination state under a schedule | Public resolution, counterparties, external payment services, operational logs, and backups require separate handling. |
| OpenETR evidence | Publish corrective or superseding evidence, or remove data where the operator controls storage | Signed evidence may have been copied and may need to remain verifiable. Correction and transparent supersession can be more accurate than claiming erasure. |
| Mainstay instance | Retire services and remove selected volumes and recovery material | Operator-owned directories, exported backups, external copies, published events, and third-party systems are outside a local teardown unless separately addressed. |

Every deployment needs a retention schedule that names the information class,
purpose, authoritative store, copies, minimum and maximum period, deletion
method, exception authority, and evidence of disposition. Backups require an
expiry and restoration policy: deleted information should not silently return
to active use after a restore.

## Deployment Privacy Record

Before serving real people, the operator should complete and maintain one
deployment privacy record. Mainstay may eventually render this record in its
operator interface, but the first version can be a reviewed document kept with
the deployment's governance material.

It should identify:

1. the accountable organization and privacy contact;
2. the population and use cases served;
3. each category of personal or potentially linkable information;
4. the specific purpose and authority for each category;
5. the authoritative component and all replicas, caches, logs, and backups;
6. local, internal, public, and external routes used by each flow;
7. every external provider and the metadata or content it receives;
8. retention, correction, deletion, and backup-expiry rules;
9. administrative roles and access controls;
10. safeguards proportionate to the sensitivity and foreseeable harm;
11. how people receive notice and exercise access, correction, withdrawal, and
    complaint rights;
12. incident contacts, breach assessment, notification, and breach-record
    procedures; and
13. the date, owner, and outcome of the last privacy review.

For an organization subject to PIPEDA, breach procedures must reflect the
current statutory regime as well as the older self-assessment tool. Records of
every breach of security safeguards involving personal information must be
maintained as required by law, and a breach posing a real risk of significant
harm may require notice to affected people and reporting to the Office of the
Privacy Commissioner of Canada.

## Product Responsibilities

### Mainstay

Mainstay should:

- make local and external service choices visible to the operator;
- preserve endpoint scope and component responsibility boundaries;
- avoid aggregating personal information merely for dashboard convenience;
- provide safe summaries instead of exposing raw user or service data;
- support a deployment privacy record, retention configuration, backup policy,
  and incident evidence without claiming to automate legal compliance;
- keep white-label branding from obscuring the accountable organization or
  privacy contact; and
- require privacy review when a lifecycle change adds a public route,
  replication target, shared mount, management endpoint, or new provider.

### Safebox Web and Acorn

Safebox Web and Acorn should:

- preserve request-scoped loading and user-controlled keys;
- explain observable metadata and external service involvement at the relevant
  workflow;
- provide clear access, export, correction, disconnection, and deletion
  semantics;
- separate public handles and evidence from private wallet or record state;
- keep sensitive values out of URLs, caches, logs, and general databases; and
- preserve explicit confirmation for consequential disclosure or value
  movement.

### Clear

Clear should:

- minimize identifying transaction metadata not required for mint operation;
- separate mint operator, root operator, treasurer, issuer, and recipient
  authority;
- document proof-state, operational, security, and financial retention; and
- expose only the bounded information required for wallet interoperability and
  accountable operation.

### Grove and Spurline

Grove and Spurline should:

- publish accurate retention, expiry, deletion, replication, logging, backup,
  and operator-access policies;
- treat encrypted content and metadata as protected information;
- support bounded collection and queries;
- avoid implying that opaque content is non-personal; and
- report deletion or expiry outcomes without promising erasure outside their
  controlled infrastructure.

### OpenETR

OpenETR integrations should:

- minimize public evidence to what verification actually requires;
- distinguish artifact identity from authorization to disclose the artifact;
- explain correlation risks of stable digests, identifiers, and event graphs;
- preserve provenance for corrections and superseding evidence; and
- leave recognition and access decisions with the authorized participant or
  institution applying policy.

## Review Triggers

A privacy review is required before:

- enabling production use or onboarding a new population;
- adding a new personal-information category or purpose;
- exposing a service outside its current endpoint scope;
- changing relay, Grove, mint, Lightning, hosting, backup, analytics, or
  monitoring providers;
- adding cross-instance replication or a new continuity destination;
- publishing new OpenETR evidence or public directory fields;
- introducing telemetry, automated profiling, AI processing, or secondary
  research use;
- changing retention, deletion, recovery, or logging behavior;
- materially changing key custody, account recovery, or administrator access;
  or
- responding to an incident, complaint, audit finding, or material legal
  change.

## Current Posture

The architecture already supports important privacy outcomes:

- local operation and local custody are practical defaults;
- ordinary attached-user wallet state is not centralized in Mainstay;
- records, attachments, wallet state, and transfers use encryption appropriate
  to their current protocol profiles;
- component responsibilities and endpoint scopes are explicit;
- application loading is increasingly resource-scoped;
- sharing and consequential operations use visible user decisions; and
- security documentation states material limitations rather than treating
  encryption as a complete privacy guarantee.

The product family is still pre-release. A production deployment also requires
operator governance that the repositories cannot supply on their own:

- a named accountable organization and privacy contact;
- documented purposes and an information inventory;
- notices and meaningful consent appropriate to the deployment;
- access, correction, complaint, and withdrawal procedures;
- retention and defensible deletion across services and backups;
- provider review and contractual allocation of responsibility;
- incident response, breach assessment, and breach records;
- staff or administrator training; and
- periodic privacy and security assessment.

The correct claim is therefore:

> Mainstay provides a privacy-supporting, local-first architecture with explicit
> component and information-flow boundaries. Each deployment remains responsible
> for lawful purpose, accountable operation, transparent external relationships,
> and the rights of the people it serves.

## Related Mainstay Documents

- [Mainstay Security](../SECURITY.md)
- [Container Interaction and Security Model](CONTAINER-INTERACTION-SECURITY-MODEL.md)
- [Ecosystem Responsibility Boundaries and Iterative Development](ECOSYSTEM-RESPONSIBILITY-BOUNDARIES-AND-ITERATION.md)
- [Identity Resolution and Event-Native Services](IDENTITY-RESOLUTION-AND-EVENT-NATIVE-SERVICES.md)
- [Mainstay Continuity Coordinator Design Note](MAINSTAY-CONTINUITY-COORDINATOR-DESIGN-NOTE.md)
- [Mainstay Grove Context Integration](MAINSTAY-GROVE-CONTEXT-INTEGRATION.md)
- [Clear Transfer Scope, Acceptance, and Authority](CLEAR-TRANSFER-SCOPE-ACCEPTANCE-AND-AUTHORITY.md)
- [Mainstay House Style and Family Audit](MAINSTAY-HOUSE-STYLE.md)
