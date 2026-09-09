---
title: Community-Led Recordkeeping and Digital Originals
description: How communities can establish authoritative digital records in context using local governance, verifiable evidence, and graduated disclosure.
---

# Community-Led Recordkeeping and Digital Originals

**Policy brief**

## Core proposition

A community should be able to decide which records are authoritative for work
within its own legitimate scope.

That does not mean inventing facts, replacing the authority that issued an
outside credential, or demanding recognition from everyone else. It means
establishing a governed local record: identifying the exact digital artifact,
recording who examined or authorized it, applying documented rules, and
preserving the evidence needed to understand its current status.

OpenETR provides the model for doing this. Mainstay provides a local house in
which a community can operate the model together.

```text
exact artifact
  -> community review and signed evidence
  -> validation under documented rules
  -> consequential state
  -> Digital Original for a defined context
```

The cryptography is new. Community recordkeeping is not.

## Authority begins in context

Communities have always maintained records whose meaning comes from their own
procedures: resolutions, appointments, permissions, registries, minutes,
certifications, benefit decisions, service records, receipts, and evidence of
completed work.

Some records originate inside the community. Others arrive from governments,
professional bodies, schools, businesses, families, or individuals. In either
case, the practical question is not whether the community controls the whole
outside system. It is whether the community has enough evidence to make the
decision for which it is responsible.

Authority is therefore bounded:

- the original issuer remains authoritative for what it issued;
- the community is authoritative for its own review, acceptance, and local
  decisions;
- the holder controls disclosure subject to applicable duties and agreements;
  and
- another institution applies its own recognition policy when the record is
  presented outside the original context.

Community-led recordkeeping does not collapse those roles. It makes them
visible.

## A scanned driver's licence

Consider a community program that needs to confirm a participant's identity or
eligibility. An authorized worker inspects a physical driver's licence,
compares it with the presenter, scans it, and records the review under the
program's policy.

The government-issued licence remains the government's credential. The scan
does not become a newly issued government licence, and the community cannot
make it valid for every legal purpose.

The scan can, however, become an authoritative **community record of that
vetting event**:

```text
exact scan
  -> cryptographic digest
  -> reviewer signature and role
  -> date, purpose, and policy
  -> expiry or re-check rule
  -> later replacement or revocation evidence
```

Under OpenETR, the exact scan is a **Digital Artifact**. Signed records
concerning its review and lifecycle form its candidate **Digital Controllable
Record**. Validation under the community's rules derives **Consequential
State**. Once that state is established, the artifact is a **Digital Original**
in the OpenETR technical sense.

For a defined, proportionate local decision, the community may now rely on its
own vetted record rather than contacting a distant service every time the same
fact is needed. A higher-risk decision, an expired record, evidence of change,
or a legal requirement for current issuer confirmation can still trigger a new
check with the issuing authority.

This is not less governance. It is governance made explicit.

## Copies are not the problem

A scanned licence, photograph, PDF certificate, or signed form can be copied
perfectly. Trying to make one set of bytes physically uncopyable is the wrong
goal.

The better questions are:

- Which exact artifact was reviewed?
- Who made the statement about it?
- Was that person or role authorized under the applicable policy?
- What evidence supports the statement?
- What status follows from the valid evidence?
- Has the record been replaced, revoked, expired, or disputed?
- Does this relying party recognize that evidence for this purpose?

A byte-for-byte copy has the same digest and therefore represents the same
Digital Artifact. Copying it does not create a new review, new authority, or
new consequential state. Editing one pixel or character produces different
bytes and a different digest.

OpenETR shifts attention from the visual appearance of a copy to the verifiable
history concerning exact content.

## A practical response to synthetic media

Synthetic images, altered documents, and convincing imitations make visual
plausibility a weak basis for trust. The useful response is not to ask software
to declare every image "real" or "fake." It is to ask a more answerable set of
questions:

```text
Is this the exact artifact that was vetted?
Who vetted or attested to it?
Under which rules?
What has happened since?
Do I recognize that authority for this decision?
```

A digest gives a simple and strong answer to the first question. Signed
evidence and community policy address the others. Once an artifact has been
properly reviewed, the digest prevents a convincing replacement from silently
taking its place. The verifier does not trust an image because it looks right;
the verifier checks that the presented bytes are the bytes the recognized
review process actually considered.

This closes several common gaps:

- silent substitution of one image or document for another;
- undetected editing after review;
- ambiguity about who made an attestation;
- loss of the policy and purpose under which review occurred;
- stale status hidden by an old screenshot; and
- dependence on the application that first displayed the record.

It does not close every gap. A reviewer can make a mistake. A signer can be
deceived, careless, compromised, or dishonest. A community can adopt a poor
policy. A synthetic artifact can be knowingly or mistakenly vetted. A digest
proves which bytes were considered, not that the scene depicted in those bytes
occurred in the physical world.

That limitation is shared by other provenance systems. The C2PA
[Content Credentials explainer](https://spec.c2pa.org/specifications/specifications/2.2/explainer/Explainer.html)
emphasizes that valid provenance does not itself decide whether assertions are
true; trust still depends on the signer, evidence, and relying context. NIST
similarly treats provenance, watermarking, detection, and other
[digital-content transparency techniques](https://www.nist.gov/publications/reducing-risks-posed-synthetic-content-overview-technical-approaches-digital-content)
as complementary approaches rather than one perfect detector.

The gain is not infallibility. It is a much smaller and more inspectable trust
surface.

## Community authority requires a rulebook

A digest becomes meaningful only when it is joined to governance. A community
recordkeeping policy should specify:

- which purposes permit a record to be created or relied upon;
- who may inspect, attest, approve, replace, revoke, or archive it;
- what evidence and review steps are required;
- how reviewer authority is appointed and withdrawn;
- which exact artifact, schema, and digest algorithm are used;
- how long the result remains current before re-checking;
- what later events change its consequential state;
- how conflicts, mistakes, appeals, and corrections are handled;
- who may see the record and under what authority; and
- which decisions still require confirmation from an external issuer.

These rules may come from a council, board, administration, professional
practice, service agreement, law, custom, or another legitimate procedure. The
terms **community**, **Clerk**, and **reviewer** describe functions; they do not
prescribe one cultural or institutional form.

This is the [Clerk function](clerk-and-treasury-functions.md) in practice:
preserving consequential records and
the evidence needed to determine what follows from them.

## Recognition stays bounded

A community can establish that a record is authoritative in its own house
without claiming universal effect.

For example, a community may recognize its vetted licence scan for admission
to a local program. A hotel may recognize a vetted guest record for an internal
service. A co-working facility may recognize a locally issued access
authorization. None of those decisions requires a court, border agency, bank,
or another community to accept the same artifact for a different purpose.

```text
OpenETR validates evidence and derives consequential state.
Community policy recognizes that state for a defined purpose.
Outside institutions decide their own recognition and effect.
```

This boundary makes community autonomy compatible with cooperation. A record
can later be presented to an outside institution together with its exact
artifact, evidence graph, policy identifier, and review history. The outside
institution can accept the community's work, request deeper evidence, contact
the original issuer, or decline recognition under its own rules.

## Graduated disclosure

Community recordkeeping should not require routine publication of sensitive
documents. Nor should every ordinary check require advanced cryptographic
selective-disclosure methods that are difficult to deploy, explain, or use
correctly.

OpenETR supports a simpler default: **graduated disclosure**.

```text
Check     -> inspect signed evidence and status
Present   -> inspect the exact artifact temporarily
Share     -> retain the artifact when deeper review is justified
Surrender -> transfer custody or control when the domain requires it
```

### Check

The artifact remains private. The relying party checks its digest-bound signed
evidence, current status, recognized reviewer, and applicable policy. Many
routine decisions should stop here.

### Present

The holder makes the exact artifact available temporarily. The verifier
calculates its digest, compares it with the vetted record, and inspects what the
decision requires without retaining a new copy by default.

### Share

The verifier receives and may retain the exact artifact because audit,
forensic review, dispute handling, or another higher-consequence decision
justifies it. Retention remains governed by purpose, authority, security, and
deletion policy.

### Surrender

Custody, control, or operative status changes. This is not merely a deeper
identity check. It requires an explicit transfer, discharge, cancellation,
revocation, or other domain-specific act.

The stages are not automatic security classifications. The community defines
which stage is proportionate to each decision, and the holder or responsible
authority participates according to the applicable policy.

## Graduated is not selective disclosure

**Selective disclosure** asks which individual attributes can be revealed
while others remain hidden. It can be valuable, particularly when a person
needs to prove a narrow fact without presenting a complete credential. It may
also require specialized credential formats, derived proofs, zero-knowledge
systems, issuer support, verifier support, and unfamiliar user decisions.

**Graduated disclosure** asks how far the verification interaction needs to
proceed. It can begin with ordinary digests, signatures, evidence records, and
policy:

```text
selective disclosure -> which facts are revealed
graduated disclosure -> how much access and verification is justified
```

The models can work together, but they should not be confused. Mainstay and
OpenETR can deliver useful graduated disclosure without making advanced
selective-disclosure cryptography a prerequisite for community recordkeeping.
Where selective disclosure is mature, understandable, and appropriate, it can
be added at a particular stage.

The practical default is:

> Check first. Present when the decision requires the record. Share only when
> retention or deep analysis is justified. Surrender only when control itself
> is meant to change.

Read OpenETR's full
[Graduated Disclosure model](https://trbouma.github.io/openetr/policy-briefs/graduated-disclosure/)
for the protocol and domain detail.

## Mainstay as the local house

OpenETR is designed to work inside Mainstay and beyond it.

Within a Mainstay deployment:

- Mainstay presents the community's record workflows, policy context, status,
  and disclosure choices;
- the Clerk function identifies the responsible authority and preserves the
  recordkeeping process;
- OpenETR identifies exact Digital Artifacts, validates DCR evidence, and
  derives consequential state;
- Acorn provides portable user keys, records, and authority;
- Grove retains encrypted, digest-addressed artifacts;
- Spurline retains and distributes signed evidence; and
- Stroma supplies the narrow signed and encrypted event format beneath those
  workflows.

Mainstay does not become the authority merely because it presents the result.
The community's rulebook and recognized actors provide authority. OpenETR
makes the resulting evidence independently verifiable. The underlying
components keep records and evidence portable beyond any one application.

This is **Our House. Our Rules. Our Business.** applied to recordkeeping: local
stewardship, legitimate and accountable procedures, and appropriate
confidentiality within the community's defined scope.

## Beyond Mainstay

The model does not depend on Mainstay. Another application, archive, registry,
wallet, professional system, or institutional service can create and verify
the same digest-bound evidence under the same OpenETR rules.

That portability matters. A community-led record should not lose its identity
or history when software changes. Nor should another relying party be forced to
trust Mainstay's database. It should be able to inspect the exact artifact,
validate the signed evidence, reproduce the consequential state, and apply its
own recognition policy.

## Confidentiality, integrity, and availability

Community-led records must preserve all three parts of the security triad:

- **Confidentiality:** sensitive artifacts are disclosed only to authorized
  people for appropriate purposes.
- **Integrity:** digests and signatures reveal substitution, alteration, and
  unsupported changes to the evidence history.
- **Availability:** authorized people can obtain and use the record and its
  verification evidence when needed, including through dependable local
  infrastructure.

Improving one property should not quietly sacrifice the others. A public
ledger may improve availability while violating confidentiality. A perfectly
private file that cannot be recovered or presented is not operationally
available. An available copy without digest verification may lack integrity.

Graduated disclosure and local-first infrastructure let the community manage
those obligations together.

## Policy implications

A community or institution considering this model should ask:

1. For which exact decisions may a community-vetted record be authoritative?
2. Which outside authority, if any, remains authoritative for the underlying
   credential or fact?
3. Who may perform the review, and how is that authority appointed, limited,
   audited, and revoked?
4. What evidence must be inspected before the artifact is accepted?
5. Which signed events establish, replace, suspend, revoke, or correct its
   consequential state?
6. How are human mistakes, compromised keys, conflicting evidence, and appeals
   handled?
7. When is local evidence sufficient, and when must the original issuer be
   consulted again?
8. What is the least disclosure required for each decision?
9. Can a verifier reproduce the result without trusting the application that
   first displayed it?
10. Can the record remain confidential, intact, and locally available through
    staff changes, software changes, and service interruptions?

These are governance questions before they are technology questions.

## Conclusion

The synthetic-media problem makes one lesson increasingly clear: appearance is
not enough. A convincing image can be false, and a plain-looking scan can be
the exact artifact a trusted process actually reviewed.

Community-led recordkeeping begins with that distinction. Preserve the exact
artifact. Record who examined or authorized it. Apply documented rules.
Maintain its consequential history. Disclose only what the decision requires.
Let each relying context decide what authority and effect it recognizes.

Human judgment remains fallible. The value of OpenETR is not that it removes
people from the process. It binds their decisions to exact content and durable
evidence so mistakes, substitutions, later changes, and differences in
authority are easier to find and harder to hide.

Mainstay gives that capability a dependable local home. OpenETR lets the record
travel beyond it.
