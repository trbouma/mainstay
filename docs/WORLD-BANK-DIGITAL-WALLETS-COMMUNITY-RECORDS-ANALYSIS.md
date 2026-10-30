# World Bank Digital Wallets and Community Record Infrastructure

Status: source analysis and proposed implementation direction  
Analysis date: 2026-10-30

Companion public brief:
[Community Wallets for Records and Phone Free Access](../website/policy-briefs/community-wallets-records-and-phone-free-access.md).

## Source and assessment scope

Tullis, Christopher; Black, David; and Cooper, Adam. 2026. *Digital Wallets:
Implementation — Practical Guidance for Deploying Wallets at National Scale*.
Digital Wallet Policy Note Series, No. 3. © World Bank.

The reviewed source is the 84-page PDF
`P505739-e3e696bc-9207-495a-bcb7-beca752f4c6b.pdf`. Page references below use
the report's printed numbering; printed p. 3 is PDF page 11. This is the
implementation note, distinct from the series' earlier trust-framework note.

This analysis separates the report's recommendations, the Mainstay design
response, and capabilities documented as implemented. Product evidence comes
from the project documents listed below, inspected on the analysis date. This
is an architectural and policy assessment, not an independent security audit
or a conformance certification.

## Overall assessment

The report provides a constructive framework for building useful wallet
ecosystems. It treats governance, issuer and verifier participation, user
experience, financing, support, and operational continuity as integral to
deployment. Its emphasis on outcomes and staged implementation is directly
relevant to Mainstay.

Safebox Web and OakGate can address many of these functional goals through a
community-first service model. Acorn provides a reusable wallet and record
runtime. OpenETR provides evidence and state-evaluation concepts applicable to
exact digital artifacts. Mainstay supplies the broader local-operation and
coordination direction.

The proposed alternative is narrower in its common technical core and broader
in the artifacts to which that core applies. It begins with records, signed
evidence, protected access, and local recognition. Specialized credential
interfaces are added for the interactions that need them. This is a design
hypothesis to validate through integration and operating costs, not a measured
claim of superiority or readiness for national-scale deployment.

## What the report recommends

| Report theme | Printed pages | Implication for a community deployment |
| --- | --- | --- |
| Real services and ecosystem outcomes | 3–4, 25–28, 31–33, 67–74 | Start with an actual service, a responsible operator, and a verifier prepared to act on the result. |
| Separate app, wallet engine, issuer, verifier, and common services | 10–14, 17–23 | Assign distinct responsibilities even when one organization operates several components. |
| Alternatives to personal smartphones | 4, 22 | Treat card, assisted, and other access paths as part of the service design. |
| Signed issuance, controlled sharing, recovery, and status changes | 34–37 | Demonstrate complete record and access lifecycles, including failure handling. |
| Layered standards and interoperability | 39–42 | Publish an explicit supported profile and test it with independent implementations. |
| Sustainable financing | 50–63, 74 | Fund staffing, maintenance, support, and foundational services as well as software. |
| Avoid vendor and integrator lock-in | 64–65 | Test replacement and migration; open source alone is insufficient. |
| Progressive deployment | 69–71 | Require evidence before moving from prototype to live sensitive services. |

The report should not be characterized as smartphone-only, limited to legal
identity, or requiring every listed standard in every deployment. It explicitly
names alternatives to smartphones, includes prescriptions and test results
among possible credentials (p. 20), and explains that implementers select a
profile from the standards menu (p. 41).

Its discussion of common trust services emphasizes CAs and PKI (pp. 14 and
21), while Figure 7 also lists trust lists, federation, vLEI, and DIDs (p. 40).
The Mainstay contribution is an explicit separation of infrastructure trust
from community recognition, rather than an assertion that the report prohibits
other trust arrangements.

## Preserve choice before fixing the architecture

The central policy takeaway is that communities at local, regional, and national
scale have choices. A decision to improve access, integrity, or accountability
does not by itself settle the appropriate credential format, certificate
hierarchy, device model, operator structure, or institutional arrangement.
Those choices should be justified by the use case and remain revisable where
their consequences permit.

The report's flexible framework, standards menu, and staged deployment approach
support this position. The following assumptions are interpretive risks that
can arise when implementing its model, rather than categorical claims made by
the authors. They are useful prompts for exploring additional implementation
paths.

### Examine the assumptions beneath a wallet project

| Possible implementation assumption | Basis in the report's framing | Constructive alternative to test |
| --- | --- | --- |
| A comprehensive trust infrastructure must precede useful participation | Common systems and assigned ecosystem roles, pp. 10–23 | Begin with bounded, accountable relationships already recognized by a community; expand recognition as cooperation develops. |
| A common technical trust hierarchy should also establish institutional authority | CA and PKI emphasis, pp. 14 and 21 | Protect connections and verify signatures while separately governing who may make which statements. |
| A credential is the default unit of trustworthy information | Issuer, holder, and verifier requirements, pp. 34–35 | Preserve exact artifacts and attach evidence so existing records can participate without mandatory format conversion. |
| An alternative form factor is sufficient to establish inclusion | Card, cloud, and paper alternatives, pp. 4 and 22 | Require complete service journeys, including recovery and assistance, without personal phone ownership. |
| Wallet control adequately represents user agency | User-controlled storage and consent-based sharing, p. 34 | Assess custody, operator discretion, delegated authority, recovery, remedy, and departure across the relationship. |
| Useful interoperability requires broad agreement on recognition | Layered interoperability, pp. 39–42 | Exchange intelligible evidence while making differences in recognition explicit; agree on common effect where the service needs it. |
| Growth primarily means extending one scheme | National deployment and ecosystem coordination, pp. 67–74 | Test cooperation among independently operable communities alongside common national services. |

The alternatives do not eliminate the underlying work. Local recognition still
requires authenticated appointments and key management. Portable evidence still
requires shared syntax and rules for interpreting statements. Card access still
requires dependable readers and services. Independent communities still need
agreements when a transaction depends on mutual acceptance.

Their value is to separate the required outcome from a particular mechanism.
For example, attributable evidence is an outcome; obtaining every signing key's
authority through one external certification hierarchy is an implementation
choice. Consistent service access is an outcome; requiring a private smartphone
is a device choice.

### Treat Mainstay as a revisable choice

This argument applies equally to Mainstay. Adopting Nostr-based events, Acorn,
OpenETR, or a particular card profile should not become an irreversible
commitment merely because the protocols are open or the deployment is local.
Small projects can create dependence on specialized knowledge, a single
maintainer, or undocumented conventions.

Mainstay's proposed advantage is a smaller common protocol set reused across
records, evidence, and community interactions. This may make the initial system
easier to understand and maintain. It remains a hypothesis until operating
experience shows that fewer mechanisms reduce total complexity rather than
move it into custom adapters, governance procedures, or application code.

An implementation should select a precise, versioned profile for reliable
operation, then preserve the capacity to change it. That means retaining exact
artifacts and signed evidence, documenting semantics, exporting recognition
policy, maintaining compatibility tests, and planning migration. Existing signed
history must remain verifiable under its original rules when new versions are
introduced. Cryptographic replacement also needs an explicit transition process;
changing algorithms cannot silently rewrite earlier commitments.

The criterion is practical substitutability: can the community replace a
component, protocol binding, provider, or access device without losing the
records, evidence, rights, and relationships it needs? Some changes will require
coordination and cost. Those consequences should be visible before adoption.

### Keep institutional possibilities open

The full institutional consequences of this infrastructure are not yet known.
Some capabilities may be familiar functions made practical again at community
scale: clerks preserving authoritative records, witnesses recording agreements,
treasuries administering bounded obligations, and associations recognizing
members. Others may emerge through cooperation among institutions that have
previously lacked a workable way to exchange evidence or share responsibility.

These are possibilities for exploration, not predicted outcomes. A protocol
does not establish the legitimacy of a new institution or show that a historical
practice remains appropriate. Communities need to evaluate who benefits, who
can contest decisions, and which safeguards must accompany a capability.

The policy concern is premature closure. Administrative arrangements inherited
from the twentieth century and assumptions embedded in early twenty-first-century
digital services should remain open to examination. A project should not settle
future governance by simply reproducing an existing registry, platform account,
or certification structure in software. Equally, novelty alone is no reason to
discard institutions that provide dependable protection and accountability.

Separate enduring responsibilities from their current implementation. Preserving
records, limiting authority, resolving disputes, and enabling participation are
responsibilities. Their division among registries, wallets, service operators,
community bodies, and external providers can evolve through explicit decisions.

### Build security into the foundation while using existing networks

The constructive security proposition is to treat confidentiality, integrity,
authorization, and verifiable history as properties to design into the records
and operations from the outset. It does not require a broad historical claim
that the internet is uniformly insecure, or that established protections can
be dispensed with.

In the proposed architecture, encrypted content limits exposure to storage and
transport intermediaries; signed, digest-bound evidence permits independent
checks of attribution and integrity; identified rules make state derivation
inspectable; and the integrating application enforces authorization before
performing an operation. OpenETR contributes evidence and rule-based evaluation,
while the surrounding components remain responsible for confidentiality,
execution, access, and availability.

This arrangement reduces the amount of authority that must be inferred from
where a record happens to be hosted or which application displays it. It does
not make a compromised endpoint safe, prevent a malicious operator from
misusing decrypted data, or prove that unseen evidence does not exist. Threat
models, secure key handling, recovery, and independent review remain necessary.

Existing browsers, HTTPS, DNS, hosting services, and networks offer reach,
familiar interfaces, and operational knowledge. Communities should be able to
use these network effects while keeping durable record identity and recognition
separate from replaceable endpoints and delivery mechanisms. An infrastructure
certificate can secure access today without determining the permanent authority
of every statement made through that access path.

The design objective is therefore to preserve the value of established networks
while limiting involuntary dependence on their particular intermediaries or
historical design choices. That is an engineering and governance discipline,
not a claim that Mainstay already achieves independence from every dependency.

### Questions before committing resources

Before adopting either a national wallet profile or the Mainstay approach,
decision-makers should establish:

1. Which outcomes are required now, and which technical choices are assumptions?
2. Which responsibilities belong to the community, its members, or outside actors?
3. What new use cases can be introduced without replacing the common foundation?
4. What information and authority would be lost if a provider or protocol changed?
5. Can another implementation reproduce the evidence evaluation and apply a
   different recognition policy without relying on the original application?
6. Which dependencies are justified by present benefits, and what is the cost
   of leaving them?
7. What evidence would cause the community to revise its initial architecture?

This makes technological choice an ongoing institutional capability. Local
communities and nation-scale programs can begin with a workable profile while
retaining the freedom to learn, cooperate, and change direction.

## Start with community responsibilities

The community-first question is which decisions people need to make together
and what evidence those decisions require. A clinic needs to distinguish a
current report from a corrected one. A clerk needs to publish an approved
resolution with a traceable amendment history. A cooperative needs to recognize
members and administer shared resources.

Each use case requires named responsibilities: who may make a statement, who
may change its status, who may view the content, and who may accept the result.
The community should document these responsibilities before choosing an
authentication provider or credential format.

Community authority is bounded by its legitimate scope and applicable
obligations. It does not guarantee acceptance elsewhere. The design should
allow external institutions to inspect the same evidence and apply their own
recognition rules, with explicit agreements where mutual recognition is needed.

## Broader record verification through OpenETR

OpenETR distinguishes exact Digital Artifacts, signed Digital Controllable
Record evidence, state derived under an identified ruleset, and recognition by
the relying context. Its format-independent model is described in the
[OpenETR overview](https://docs.openetr.org/). The model permits portable
evidence concerning a file without requiring its contents to be rewritten as
a credential.

For a proposed community deployment, verification should answer separate
questions:

1. **Content integrity:** do the obtained bytes match the expected digest?
2. **Evidence validity:** are the relevant signed statements structurally and
   cryptographically valid?
3. **Derived state:** what follows under the specified rules, given the evidence
   actually available and the evaluation context?
4. **Recognition:** does this community recognize that actor and statement for
   this purpose?
5. **Effect:** what action may the service take under its rules and obligations?

A correct digest does not establish a true diagnosis. A valid signature does
not appoint a municipal clerk. An accessible file is not necessarily authorized
for disclosure. Keeping these questions separate makes a broader scope of
verification possible without conflating technical checks with authority.

| Illustrative artifact | Evidence and state to evaluate | Responsibility that remains outside generic verification |
| --- | --- | --- |
| Lab report in PDF or structured form | Exact content, author statement, correction or withdrawal evidence | Clinical interpretation, patient matching, confidentiality, and professional authority |
| Council resolution or public notice | Adopted version, clerk's statement, amendment and publication history | Decision-making procedure, mandate, publication duties, and redaction |
| Membership or benefit record | Issuance, scope, expiry, and status evidence | Eligibility rules, appeals, and participating providers' acceptance |
| Inspection photograph or report | Exact bytes, attributable observations, linked supporting evidence | Whether the inspection occurred properly and satisfies the relevant requirements |
| Native VC or mdoc | Exact original bytes plus supported native verification and contextual evidence | Scheme-specific validation, assurance, and recognition |

These are proposed domain uses, not a claim that a generic verifier is already
a clinical system, public registry, or universal credential verifier. Record
schemas, terminology, access controls, and domain rules remain necessary.

### Current evidence evaluation in Safebox Web

The current migration note documents an implemented OpenETR Core Record
Ruleset 1.0 evaluator. It validates anchors and linked publisher notices,
retains conflicting branches, and distinguishes a missing anchor from an
unavailable check. It reports each qualifying publisher's position separately.
Recognition and legal or operational effect remain unevaluated.

The note also records important retrieval limits. Queries are bounded and
unpaginated; completeness remains unknown. A supplied metadata digest is not
described as a fresh hash of retrieved file bytes. A current-looking display
therefore must not be interpreted as proof that all relevant evidence has
been found. The implemented-policy section supersedes older roadmap text
elsewhere in that note. See [S1].

This is a useful foundation for community trust adapters: it already separates
what the evidence supports from what a community must decide. Formal recognition
adapters and broader domain-state workflows remain development work.

## Separate WebPKI from community recognition

Three trust questions should be visible in the architecture:

| Layer | Question | Possible mechanism |
| --- | --- | --- |
| Connection and infrastructure | Are we communicating with the intended endpoint over a protected channel? | HTTPS and WebPKI, plus service authentication or pinning where required |
| Evidence | Which key signed this exact statement concerning this artifact? | Signature and digest validation, explicit event links, versioned rules |
| Community recognition | Is that actor authorized and accepted for this purpose? | Accountable appointments, recognized-key lists, scoped delegations, local policy, and review |

A CA is not a mathematical prerequisite for signing data or checking a
signature against a known public key. The difficult question is how that key
becomes recognized as representing a particular actor and scope. A community
can answer through its own authenticated governance process instead of
requiring an external X.509 certification hierarchy for every record signer.

For example, a community can appoint a records clerk, verify the clerk's public
key through an established channel, and document the kinds of statements the
clerk may make. Verifiers can use that recognition policy alongside OpenETR
evidence. The same clerk's application may still use an ordinary HTTPS
certificate. Changing the web host or TLS certificate should not silently
change the clerk's record-signing authority.

The community must then operate the responsibilities it has accepted:

- authenticate the initial key-to-role binding and distribute trusted policy;
- define scope, duration, delegation, and succession;
- protect signing keys and handle compromise and replacement;
- define when withdrawals and policy changes take effect;
- retain history needed to evaluate earlier statements;
- resolve disputes and conflicting assertions; and
- establish recognition arrangements with other communities where needed.

OpenETR carries evidence for evaluation; it does not create the mandate or
select a universally trusted community root. A signed appointment is useful
only when the verifier already has a justified basis for recognizing its
appointing authority. External certificates can remain optional inputs to
this policy and can be required for specific external schemes.

This is separation of trust responsibilities, not removal of operational
dependence. In current browser deployments, a compromised application origin
can still compromise sessions and disclosure. Removing an external CA from
record recognition does not make HTTPS, hosting, DNS, authentication, or
custody security unimportant.

## Define the smaller common technical core

The proposed reduction is in the number of mandatory record-specific
mechanisms a community must operate before it can deliver useful services.

| Common responsibility | Proposed reusable foundation | What still needs a specialized profile |
| --- | --- | --- |
| Identify content | Exact bytes and cryptographic digests | Canonicalization when a domain needs semantic rather than byte equivalence |
| Attribute statements | Public-key signed events through the family's Nostr/Stroma implementation | External signature suites and credential formats when required |
| Derive record state | OpenETR evidence and named, versioned rules | Domain lifecycle rules and recognition inputs |
| Safeguard and exchange records | Acorn, encrypted records and attachments, relay and blob services | Purpose-specific authorization, retention, and disclosure policy |
| Reach people | Browser workflows, NFC and QR entry points | Tested reader/browser support, accessible terminals, and assistance |
| Connect other schemes | Adapters at defined boundaries | Required issuance, presentation, assurance, and semantic specifications |

OpenETR and family protocols are open specifications with implementation work;
they should not be presented as having the same adoption, testing breadth, or
formal status as established international standards. A simpler local core
can still impose integration costs at its boundaries. Its benefit must be
demonstrated through fewer bespoke workflows, understandable operations,
independent verification, and reliable replacement.

Preserve existing credential bytes when receiving them. Safebox Web's documented
VC, PID/mdoc, and mDL previews are explicitly previews, not proof of native
signature validation [S2]. An OpenETR statement about an imported credential
does not replace its native scheme checks. Likewise, proving a PDF's integrity
does not provide selective disclosure of fields inside that PDF.

## Map requirements to the product family

| World Bank objective | Relevant capability or direction | Current qualification |
| --- | --- | --- |
| Usable holder application | Safebox Web record/payment interface; OakGate managed wallet | Documented working foundations; user testing and deployment assurance still matter |
| Secure record handling and sharing | Acorn-mediated keys, protected records and attachments; app sharing flows | Custody and session boundaries differ between applications |
| Issue and receive useful records | OakGate record creation/sharing and card-directed receipt | Receipt proves delivery, not truth or recognized authority [O1, O2] |
| Practical verification | Safebox Web OpenETR anchor/notice evaluation; OakGate presentation of records and OpenETR information | Evidence retrieval is bounded; recognition remains separate [S1, O1] |
| Alternatives to smartphone ownership | OakGate card payments, receipt, presentation, and enrolled login; Safebox card login | Current services require connectivity; device support must be tested |
| Recovery after device loss | Revocable card credentials, recovery disclosure and underlying Acorn architecture | OakGate independent restore rehearsal and full Go Independent workflow remain outstanding [O3] |
| Interoperability and portability | Shared Acorn foundation, exact artifacts, signed evidence, supported cross-home flows | Automated cross-home coverage does not establish live interoperability everywhere |
| Resilience | Local services, retained evidence, backups, alternative user devices | Complete local and offline service profiles are not established by architecture alone |
| Accountability and sustainable operation | Mainstay governance principles, defined operators, support and recovery procedures | Staffing, financing, audits, and dispute resolution require actual institutional arrangements |

This is a functional alignment map. It does not claim that the products satisfy
all requirements of a national wallet scheme, health-record deployment, or
regulated service.

## NFC as a full substitute for personal phone ownership

### The policy goal

A fully empowered card should give its holder access to the complete set of
supported community services without requiring a personal phone. Equal
participation includes enrollment, receiving and presenting records, supported
payments, reviewing activity, obtaining help, and recovering from card loss.
The cardholder should retain an individual account even when using a shared
phone or an assisted terminal.

The unit of comparison is the card plus reader and service, just as a phone
wallet depends on software and infrastructure. A passive card does not itself
provide a screen, private confirmation channel, processor for the whole wallet,
or storage for all records. Those capabilities must be supplied accessibly.

### OakGate's implemented route

OakGate documents a paired card that carries a revocable encrypted credential,
issuer-routing information, and a pinned service public key. The private key,
funds, and records remain off-card in the supporting custodial wallet system.
Supported flows include payments, receipt of funds, presentation of selected
record categories, card-directed record receipt, and separately enrolled
Keycloak login [O1–O4].

Card-directed receipt is a concrete inclusion feature. An issuer scans the
recipient's card, confirms the destination, and delivers the record through
Acorn. The recipient needs no phone. Delivery handling includes persistent
journals and explicit status checks for uncertain outcomes rather than blindly
repeating an import [O2].

The capability brief records deployment confirmation for local NFC record
sharing, while cross-home flows have automated coverage and still need live
acceptance testing between independent homes [O1, O3].

### Safebox Web's distinct route

Safebox Web documents card issuance, activation, revocation, and PIN-gated
login. Its card contains an application-encrypted Acorn bootstrap credential,
including private-key material, unlike OakGate's custodial reference. The
application checks the card generation and PIN before establishing a session.
This is a root-authority credential encrypted for the issuing application,
not an independently signing smart card [S3].

Dedicated card-based record retrieval and separately approved disclosure are
specified as a design proposal. Existing login and ordinary record capabilities
are useful foundations but do not demonstrate completion of those dedicated
flows [S4]. Card formats, key custody, recovery, and assurance should therefore
not be described as interchangeable across the two applications.

### Assurance and shared-device boundaries

The low-cost memory tags used in these designs can be copied. Encryption
protects payload contents and integrity but does not make the physical tag
unclonable. OakGate's current payment and record flows are PIN-free; enrolled
login uses separate policy. Safebox login uses a PIN and persistent attempt
limits, but a copied active credential plus its PIN remains usable until
restricted by the service [O4, S3].

Before expanding sensitive access, deployments need action-specific
authorization, a trustworthy display of the requested action, and proportionate
protection against copied cards or malicious readers. Health content should
not become available merely because an ordinary payment terminal can read a
card. Emergency disclosure needs an explicit, narrowly scoped policy and
accountability.

For shared devices, test whether the next user can see the previous person's
session, downloads, previews, clipboard contents, or record history. A kiosk's
private browsing mode alone does not protect against a compromised host.
Provide assisted recovery and card suspension that do not require the lost
card, a private phone, or cooperation from the owner of a shared phone.

These controls make the promise of equal participation credible. They are
acceptance criteria for full service parity, not reasons to limit the card to
a second-class credential.

## Distinguish forms of resilience

| Condition | Potential response | Evidence or limitation to retain |
| --- | --- | --- |
| Holder has no phone or a flat battery | Card and accessible participating reader | Reader, screen, power, and service availability still required |
| Household shares one phone | Separate member credentials and short-lived sessions | Test account separation and confidential assistance |
| Public internet path fails | Locally operated services where fully provisioned | Test authentication, DNS/TLS, custody, relays, blobs, status, and authorization together |
| Evidence source is temporarily unavailable | Evaluate retained signed evidence where policy allows | Disclose evidence age and retrieval limits; later changes may be unknown |
| Issuing home is unavailable | Recovery or explicitly designed continuity arrangements | Current OakGate online authorization is not replaced by possessing the card |
| Card is lost or copied | Revoke and replace under documented recovery procedures | Terminate or constrain related sessions where policy requires; test the behavior |
| Provider exits or infrastructure moves | Restore identities, records, evidence, and policy on replacement infrastructure | Verify recovery and routing; portable data alone does not migrate all service state |

Offline verification and offline authorization are different capabilities. A
retained signature can remain verifiable while current revocation or payment
state is unavailable. A service must state whether it can proceed with bounded
staleness or must defer. Health decisions, record presentation, and spending
need different policies.

OpenETR can contribute to evidence continuity when the necessary artifacts,
signed history, rules, and recognition inputs are retained. It does not restore
missing encrypted content, discover every unseen event, or eliminate the need
for controlled access and backups.

## Deployment and financing proposal

Apply the report's phased approach to a small community service before making
broader claims. Begin with non-sensitive sample records and low-consequence
transactions. Include people without phones, shared-phone users, staff, and
independent verifiers in the design and acceptance work.

Fund the whole service: cards and replacements, readers, hosting, local power
and connectivity, staff assistance, updates, security review, recovery drills,
and dispute handling. A low-cost card does not imply low total operating cost.
Community, cooperative, public, or service-based funding can be considered;
the proposal does not assume that charging for each verification will sustain
the system.

Keep the recognition rules and evidence exportable. Train more than one operator
and demonstrate a component replacement. This addresses the report's warning
that open-source deployments can still become dependent on one integrator or
a small pool of maintainers (pp. 64–65).

## Acceptance checks for a pilot

1. Complete enrollment, record receipt, presentation, activity review, help,
   and card replacement with no privately owned phone.
2. Demonstrate two people using one device without crossing sessions,
   records, or authorization boundaries.
3. Have an independent verifier hash the actual artifact and evaluate the
   exported evidence under the same identified rules; preserve conflicts and
   unknown retrieval completeness.
4. Recognize a properly appointed local signer without an external CA-issued
   record-signing certificate. Reject a valid signature from an unrecognized
   or out-of-scope key while keeping normal TLS verification enabled.
5. Test amendment, withdrawal, signer replacement, policy change, and stale
   evidence with explicit evaluation times and outcomes.
6. Test copied-card use, lost-card suspension, exhausted PIN attempts, and
   sensitive disclosure from an untrusted terminal.
7. Break the public internet route, the home service, and an evidence source
   separately. Show which operations remain available and which are deferred.
8. Recover the same wallet and records from tested backups. Verify custody
   and access boundaries rather than treating recovery disclosure as a restore.
9. Test cross-home operation with independent deployments and real devices,
   including uncertain delivery and duplicate requests.
10. Measure successful task completion, assistance required, time to replace
    a card, access failures, verification uncertainty, and total operating cost.
11. Replace a component or provider while preserving the same artifacts,
    signed history, and recognition policy. Record the migration effort and
    identify dependencies that still prevent a practical exit.
12. Add a second record use case with different recognition rules. Determine
    whether the common core can support it without imposing the first use
    case's institutional assumptions or requiring an incompatible redesign.

These checks translate the proposed benefits into outcomes. Broader scope,
simplicity, resilience, and inclusion should be demonstrated by completed user
journeys and reproducible evidence.

## Sources and implementation references

**World Bank source:** the supplied implementation note cited above. The most
important evidence anchors are printed pp. 4 and 22 for inclusion; pp. 12–14
for components; pp. 20–21 for credential scope and trust services; pp. 34–37
for requirements; Figure 7 and pp. 39–42 for standards; pp. 50–63 for financing;
pp. 64–65 for lock-in; and pp. 67–74 for deployment and conclusions.

**Safebox Web:**

- [S1 — Implemented OpenETR verifier policy and terminology migration](https://github.com/trbouma/safebox-web/blob/main/docs/OPENETR-ANCHOR-STANDING-TERMINOLOGY-MIGRATION-NOTE.md).
- [S2 — Project status and native-format preview boundaries](https://github.com/trbouma/safebox-web/blob/main/website/project-status.md).
- [S3 — NFC card issuance and PIN-gated login](https://github.com/trbouma/safebox-web/blob/main/website/nfc-card-design.md).
- [S4 — Card record retrieval and disclosure proposal](https://github.com/trbouma/safebox-web/blob/main/website/card-record-retrieval-design.md).

**OakGate:**

- [O1 — Card capabilities and implementation distinctions](https://github.com/trbouma/oakgate/blob/main/docs/card-capabilities-policy-brief.md).
- [O2 — Card-directed record sharing and delivery handling](https://github.com/trbouma/oakgate/blob/main/docs/040-nfc-record-sharing.md).
- [O3 — Project status and outstanding acceptance checks](https://github.com/trbouma/oakgate/blob/main/docs/project-status.md).
- [O4 — Card trust, custody, and security boundaries](https://github.com/trbouma/oakgate/blob/main/docs/029-nfc-card-trust.md).

**OpenETR and Mainstay:**

- [OpenETR model and recognition boundary](https://docs.openetr.org/).
- [OpenETR roadmap](https://docs.openetr.org/openetr/roadmap/).
- [Mainstay product-family responsibilities](../website/product-family.md).
- [Mainstay continuity model](../website/continuity.md).
- [Clarity of Priority](../website/policy-briefs/clarity-of-priority.md).
- [Community Purpose and Personal Privacy Terms](../website/policy-briefs/community-purpose-and-personal-privacy-terms.md).
