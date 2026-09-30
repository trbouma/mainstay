# Data Sovereignty in Practice: Analysis for Mainstay

Status: source analysis  
Analysis date: 2026-09-29

## Source

World Economic Forum Global Future Council on Data Frontiers, *Data
Sovereignty in Practice*, briefing paper, September 2026, 17 pages.

The paper is a collaborative diagnostic rather than a prescriptive framework.
It maps sovereignty claims, operating models, trade-offs, and failure modes
across individuals, communities, institutions, states, regional groupings, and
technology platforms. This note first represents that argument on its own terms
and then evaluates where it supports, qualifies, or challenges Mainstay.

## Executive assessment

The paper provides strong conceptual support for Mainstay's local-first and
federated architecture. Its central claim is that sovereignty is credible only
when legitimate authority aligns with practical capability. Rights without
control are difficult to exercise; technical control without a legitimate
mandate is not sovereignty; and collaboration becomes dependency when it lacks
transparency, accountability, or a workable exit.

That model fits Mainstay's distinction between community authority and
technical operation. Mainstay does not create jurisdiction, appoint legitimate
decision-makers, or give a record or unit of value universal standing. It gives
an authorized community or institution practical capabilities for keys,
records, exchange, storage, signed events, recovery, and local continuity. Its
component boundaries are intended to keep authority visible rather than
absorbing it into one application or platform.

The paper also sharpens the standard Mainstay must meet. Local hosting, open
source, encrypted storage, or portable keys are instruments, not proof of
sovereignty. A deployment is credible only if its operator and affected people
can understand the control set, audit important actions, rotate keys, recover
state, enforce policy, obtain redress, and leave or replace providers without
unreasonable friction. An open stack without security, maintenance, and
integration capacity may be less resilient than a well-governed commercial
service.

The paper therefore supports Mainstay's direction while taking away any easy
claim that Mainstay is inherently sovereign. It supplies a better formulation:
Mainstay is infrastructure for exercising legitimate authority and building
practical capability under conditions of cooperative interdependence. Whether
a particular deployment achieves meaningful sovereignty remains an evidence-
based governance and operational question.

## The paper's framework

### Sovereignty is a capacity, not a binary condition

The paper rejects the reduction of data sovereignty to localization. Where
data is stored and which law applies matter, but sovereignty also depends on
infrastructure, connectivity, compute, models, identity, access controls,
auditability, portability, enforcement, institutional competence, and redress.

Its working definition is the capacity of individuals, communities,
institutions, and states to exercise legitimate rights, technical control, and
accountable governance over data in which they have an interest while enabling
trusted, equitable, interoperable collaboration.

This produces three implications:

1. sovereignty exists by degree and can strengthen or weaken over time;
2. cross-border or shared infrastructure can preserve sovereignty when
   authority and capability survive the relationship; and
3. sovereignty must be assessed across the complete technical and
   institutional stack.

### Data has several technical states

The paper follows data across three states:

| State | Infrastructure | Sovereignty questions |
| --- | --- | --- |
| Data at rest | Storage | Residency, encryption, retention, and access rights |
| Data in motion | Connectivity | Cross-border transfer, interoperability, and secure routing |
| Data in use | Compute | Training, inference, audit logs, privileged access, and downstream applications |

Digital identity, governance, access controls, and standards cut across all
three. This is important because a system may store data locally while remote
providers still control processing, model updates, privileged access, keys, or
service continuity.

### Sovereignty claims are layered

The paper identifies six kinds of claim:

- **individual agency**, grounded in privacy, dignity, consent, and redress;
- **community stewardship**, grounded in cultural integrity, collective
  benefit, and self-determination;
- **institutional resilience**, grounded in continuity, compliance, and
  operational control;
- **state sovereignty**, grounded in jurisdiction, security, public interest,
  and industrial policy;
- **regional and development sovereignty**, grounded in pooled capacity,
  bargaining power, and strategic autonomy; and
- **platform power**, the de facto sovereignty exercised through technical
  architecture, access conditions, models, APIs, and intellectual property.

The paper does not give all claims equal standing. It argues for context-
specific governance fitted to the data, community, and use case. This guards
against treating state jurisdiction, platform control, community stewardship,
and individual consent as interchangeable.

### Authority and capability must align

The paper's most useful analytical device is a two-axis model:

| Authority | Capability | Result |
| --- | --- | --- |
| High | High | Credible sovereignty |
| High | Low | Rights without control; claims may be unenforceable |
| Low | High | Control without mandate |
| Low | Low | Weak or absent sovereignty claim |

Authority concerns who has legitimate standing to decide. Capability concerns
who controls infrastructure, access, keys, logs, updates, portability,
enforcement, incident response, and exit. Governance capacity and legitimacy
connect the two.

The practical unit is not abstract ownership of copyable data but enforceable
rights: access, constraints on use, audit, onward-transfer limits, and exit
without unreasonable friction. Each can fail at a different point in the data
lifecycle.

## Operating models and their lessons

The paper presents five models without declaring one universally superior.

### Indigenous data governance

The CARE Principles, Traditional Knowledge and Biocultural Labels, and
emerging provenance standards provide mechanisms for collective preferences,
reuse conditions, and benefit-sharing. The paper treats Indigenous data
governance as the most developed operational toolkit in the field and as a
source of lessons beyond Indigenous contexts.

For Mainstay, this supports community-led policy, provenance, collective
authority, and bounded disclosure. It also reinforces an existing caveat:
specific First Nations, Inuit, Metis, and other Indigenous frameworks must not
be collapsed into a generic sovereignty label.

### Data embassies

An institution may place data, workloads, or compute in another jurisdiction
while preserving home-country law and safeguards through explicit legal and
technical arrangements. This relocates and formalizes risk rather than
eliminating it.

This supports Mainstay's view that local-first is not local-only. A hosted or
external route can contribute to continuity when identities, keys, audit,
policy, and exit remain governable.

### Community-controlled language data

Language initiatives demonstrate that access and representation are
insufficient without consent, provenance, governance capacity, and benefit
return. A locally relevant model can still reproduce extraction when an
outside provider controls training, deployment, or commercialization.

This expands Mainstay's privacy model: trustworthy custody must include
purpose, downstream use, derived artifacts, and benefits, not only encrypted
storage.

### Regional AI infrastructure

Regional models can improve representation and build capability, but a model
served entirely by foreign cloud infrastructure leaves continuity, updates,
and incident response elsewhere. Relevance at the model layer does not prove
control across the stack.

The parallel for Mainstay is direct. Local branding, community data, or a
community-facing application does not make an installation locally governable
if key operational dependencies remain opaque or immovable.

### Data commons

Collaboratively governed data ecosystems allow communities to pool data while
retaining rules for access, purpose, and conditions. The model demonstrates
sovereignty through governance and negotiated interdependence rather than
isolation.

This aligns with Mainstay's cooperative independence and with cross-community
recognition through OpenETR, provided each participant's authority, evidence,
acceptance policy, and exit remain visible.

## Sovereignty-washing

The paper defines sovereignty-washing as marketing sovereignty while material
control and value remain outside the customer's or community's reach. Its
diagnostic checklist asks:

- Can data be exported, models ported, and encryption keys rotated without
  vendor assistance?
- Do model weights, update schedules, and inference infrastructure remain
  externally controlled?
- Does delivered service match the contracted version, precision, and
  throughput?
- Are subcontractors and cross-border toolchains disclosed and auditable?
- Can a vendor unilaterally push consequential changes or end service?
- Are access, processing, and transfer events independently verifiable?
- Does local storage provide meaningful transparency, rights, and recourse?
- Do pricing structures penalize local processing and bias users toward an
  external default?

This checklist should be applied to Mainstay itself. Terms such as
**local-first**, **portable**, **private**, **community-governed**, and
**sovereign** must describe testable properties rather than aspirations.

## Where the paper supports Mainstay

### 1. Cooperative independence

The paper's **trusted interdependence** closely matches Mainstay's cooperative
independence. Most communities and institutions cannot and need not reproduce
every layer locally. They can use shared infrastructure and outside services
while preserving accountable choice, portability, and a credible route out.

### 2. Authority is not the application

Mainstay separates the authority of a community, issuer, reviewer, or
institution from the software presenting its state. The paper validates this
separation by treating capability without mandate as control, not sovereignty.

### 3. Full-stack assessment

Mainstay's family structure spans authority and keys, records, exchange,
storage, connectivity, service identity, routing, recovery, and user
experience. This is better aligned with the paper's full-stack model than a
data-residency-only claim.

### 4. Stable identity and exit

Mainstay distinguishes durable service identities, artifact digests, wallet
keys, and mint keysets from replaceable endpoints. That design supports the
paper's exit-right requirement because routes and providers can change without
silently changing the underlying identity.

### 5. Verifiability

Signed events, content digests, service attestations, supply evidence, and
OpenETR consequential state can make important claims independently
inspectable. This supports the paper's rule that a sovereignty claim must be
auditable rather than merely contractual or promotional.

### 6. Community stewardship

Mainstay's Clerk and Treasury framing gives communities tools to express
recordkeeping and exchange policies without prescribing one institutional
form. This fits the paper's layered and context-specific model of sovereignty.

### 7. Local continuity

A local Mainstay instance can keep selected capabilities available when an
outside route or provider is unavailable. That is practical institutional
capability rather than data localization for its own sake.

## Where the paper qualifies or challenges Mainstay

### 1. Mainstay does not confer sovereignty

Software cannot supply legitimate authority. A club, council, government,
issuer, or reviewer must already possess or obtain the mandate it exercises.
Mainstay can strengthen capability and make authority legible; it cannot cure
an invalid mandate.

### 2. Local operation can still be dependent

A locally running container may depend on remote source repositories, external
relays, vendor-controlled mobile platforms, upstream models, opaque base
images, or expertise available only from one developer. Local execution is not
the same as independent operation.

### 3. Open source transfers responsibility

Mainstay's open components improve inspection and replacement, but the operator
inherits patching, monitoring, key custody, backup, integration, and incident
response. Without adequate people and procedures, openness may expose a
capability gap rather than close it.

### 4. Community authority can conflict with individual rights

Collective stewardship does not erase privacy, consent, access, correction,
appeal, or redress. Mainstay policy must make the relationship among individual,
community, institutional, and state claims explicit rather than treating
"community-governed" as dispositive.

### 5. Data use extends beyond stored artifacts

Encryption and local custody do not govern inferences, model training,
telemetry, derived datasets, screenshots, exports, or decisions made from data.
Purpose limitation and downstream conditions require policy and evidence beyond
the storage layer.

### 6. Cross-community exchange creates new dependencies

Federation can expand capability while diluting control. OpenETR recognition,
Clear acceptance, relay exchange, and shared hosting need explicit rules for
authority, audit, benefit, incident response, onward transfer, and exit.

### 7. Recovery and redress remain incomplete if only technical

Restoring keys and databases is necessary but not sufficient. A credible
deployment also needs understandable complaints, correction, dispute,
revocation, governance succession, and exceptional-access processes.

### 8. Full localization can be disproportionate

The paper warns that isolated infrastructure loses economies of scale and may
reduce quality or resilience. Mainstay should place components locally when
risk, continuity, law, culture, or governance justifies it, not make universal
self-sufficiency the objective.

## Product-family mapping

| Sovereignty concern | Mainstay capability | Evidence required | Residual risk |
| --- | --- | --- | --- |
| Legitimate authority | Installation and service commissioning, signed policy evidence | Appointments, scopes, signatures, revocation and audit | A valid key may still represent an invalid or expired mandate |
| Identity and access | Acorn keys and service identities | Portable keys, recovery tests, access policy | Device compromise, coercion, inaccessible recovery |
| Data at rest | Grove and local persistent storage | Encryption, content digests, retention, backup and deletion tests | Metadata, administrator access, physical compromise |
| Data in motion | Stroma, Spurline and route resolution | Signed events, encryption, route policy and delivery evidence | Traffic analysis, relay policy, onward transfer |
| Data in use | Safebox Web, Clear and external applications | Purpose rules, audit logs, processing inventory | Inference, exports, telemetry, external compute |
| Record recognition | OpenETR evidence and consequential state | Exact artifacts, validation rules, reviewer authority | Recognition remains bounded; reviewers can err |
| Exchange | Clear Mint Notes and treasury controls | Issuance authority, supply evidence, acceptance and settlement policy | Issuer default, lost proofs, mistaken acceptance |
| Continuity and exit | Mainstay lifecycle, backups and replaceable routes | Restore drills, migration tests, key rotation and component substitution | Skills shortage and hidden upstream dependencies |

## A Mainstay sovereignty test

A deployment should not describe itself as sovereign without answering:

1. **Authority:** Who has standing to decide, and how is that mandate evidenced,
   limited, reviewed, and revoked?
2. **Individuals:** What consent, access, correction, appeal, and redress can an
   affected person exercise?
3. **Community:** What collective interests apply, who represents them, and how
   are dissent and benefit-sharing handled?
4. **Control set:** Who controls infrastructure, administrator access, keys,
   updates, logs, backups, routes, and recovery?
5. **Data lifecycle:** What happens to data at rest, in motion, and in use,
   including derived data and model training?
6. **Audit:** Can independent reviewers verify access, processing, issuance,
   transfer, recognition, and policy changes?
7. **Portability:** Can identities, artifacts, events, proofs, policies, and
   operational state move in usable forms?
8. **Exit:** Can the operator rotate keys and replace a provider or component
   without unreasonable vendor assistance or rebuilding dependent systems?
9. **Continuity:** Have outage, restore, compromised-key, administrative-change,
   and vendor-loss scenarios been exercised?
10. **Interdependence:** Which external relationships are necessary, and are
    their terms transparent, reversible, and proportionate?
11. **Capability:** Does the operator have the skills, budget, documentation,
    and staffing to discharge the responsibility it has assumed?
12. **Claims:** Are public descriptions no stronger than the evidence supports?

## Recommended changes to Mainstay policy and practice

1. **Describe Mainstay as sovereignty-enabling, not inherently sovereign.** A
   deployment combines legitimate authority and proven capability; software
   alone supplies neither legitimacy nor complete independence.
2. **Document the control set.** Add an operator-visible inventory of keys,
   privileged accounts, update channels, endpoints, subcontractors, external
   services, recovery material, and responsible roles.
3. **Make exit testable.** Define component-level export, migration, key
   rotation, and substitution tests and include them in release acceptance.
4. **Extend privacy review to data in use.** Track telemetry, inference,
   derived data, exports, and model-training eligibility, not only stored
   records and network encryption.
5. **Add governance evidence to health reporting.** Technical health should be
   distinguished from commissioning, current authority, policy validity, and
   recognition status.
6. **Provide layered rights and recourse.** Document individual, collective,
   institutional, and external-authority claims for each use case, including
   who resolves conflicts.
7. **Stress-test sovereignty.** Exercise internet loss, upstream repository
   loss, vendor outage, compromised keys, hostile or mistaken administrative
   change, restore, and component replacement.
8. **Measure operator capability.** A production profile should state required
   skills, patch and incident responsibilities, recovery objectives, and
   support arrangements.
9. **Keep localization proportionate.** Select local, hosted, or shared
   infrastructure according to the actual risk and community need while
   preserving accountable choice.
10. **Adopt a sovereignty-washing review.** Require each claim such as local,
    private, portable, community-governed, and resilient to cite a test or
    operating control.

## Strengths of the paper

- It gives sovereignty a practical authority-capability test.
- It recognizes individual, collective, institutional, state, regional, and
  platform power without collapsing them.
- It treats exit, audit, portability, and redress as central rather than
  secondary.
- It avoids equating sovereignty with isolation or total self-sufficiency.
- It treats Indigenous data governance as a substantive source of operational
  methods rather than a peripheral example.
- Its sovereignty-washing checklist converts broad claims into due-diligence
  questions.
- It openly recognizes the costs and capacity requirements of localization and
  open infrastructure.

## Limitations and unresolved questions

- The briefing is conceptual and does not provide a maturity model, metrics,
  empirical case comparisons, or implementation sequence.
- Its treatment of conflicts among individual, community, state, and platform
  claims remains high-level.
- It identifies legitimate authority but offers limited guidance for disputed
  representation, internal dissent, overlapping jurisdiction, or capture.
- The paper discusses benefit-sharing but does not specify accounting methods
  for value derived from data.
- Cybersecurity appears throughout, but concrete assurance, threat models, and
  minimum controls remain outside scope.
- The authority-capability matrix can make sovereignty appear more stable than
  it is; both axes vary by data class, purpose, time, and affected party.
- The paper relies mainly on expert synthesis and illustrative models rather
  than systematic evaluation.

These limitations do not weaken the diagnostic. They identify the work needed
to turn it into an operational assurance framework.

## Proposed Mainstay policy position

Mainstay can state:

> Mainstay supports communities and institutions in aligning legitimate
> authority with practical digital capability. It does not make an operator
> sovereign by installation, require isolation, or eliminate interdependence.
> It makes authority, identity, custody, recognition, exchange, routing, and
> recovery more explicit and portable so that collaboration can remain
> accountable and reversible.

This position is consistent with four rules:

1. **Authority must be legitimate and visible.** Technical control is not a
   mandate.
2. **Capability must be demonstrated.** Rights that cannot be exercised,
   audited, recovered, or exited remain incomplete.
3. **Sovereignty is layered and proportionate.** Different actors hold distinct
   claims, and not every component must be local.
4. **Interdependence must preserve choice.** Shared services are compatible
   with sovereignty when relationships are transparent, governable, and
   reversible.

## Conclusion

*Data Sovereignty in Practice* supports Mainstay's deepest architectural
instinct: a community needs more than abstract rights or remote assurances. It
needs practical, inspectable capability close enough to govern, recover, and
use. The paper also supports Mainstay's refusal to equate local-first with
isolation and its separation of authority from applications and providers.

At the same time, it raises the evidentiary bar. Mainstay cannot rely on local
hosting, open source, encryption, or community language as proxies for
sovereignty. Each claim must survive a full-stack assessment of authority,
control, audit, downstream use, portability, recourse, operator competence,
and exit.

The resulting position is stronger and more honest: Mainstay is not sovereignty
in a box. It is a coordinated set of capabilities through which legitimate
communities and institutions can exercise greater agency while continuing to
cooperate with people and systems beyond their local boundary.

