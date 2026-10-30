---
title: Community Wallets for Records and Phone Free Access
description: A community-first response to World Bank digital wallet guidance through Safebox Web, OakGate, OpenETR, and inclusive NFC access.
---

# Community Wallets for Records and Phone Free Access

**Policy brief · 30 October 2026**

## Core proposition

Digital wallets should help people participate in community life: receive and
present records, access services, move value, and understand the evidence behind
important decisions. Personal smartphone ownership should not determine whether
someone can participate fully.

Mainstay approaches these goals through Safebox Web and OakGate, supported by
Acorn and the broader product family. OpenETR provides a general model for
verifiable evidence concerning records. Together, these offer a path toward
community-operated infrastructure with a small reusable technical foundation,
clear local authority, and access through browsers and NFC cards.

> Build useful community capability first. Make participation independent of
> personal phone ownership. Keep evidence portable and recognition accountable.

This is a complementary implementation direction for the World Bank's
*Digital Wallets: Implementation — Practical Guidance for Deploying Wallets at
National Scale*. The report emphasizes useful services, inclusion, open
standards, sustainable operations, and phased deployment. Those goals also
provide a sound basis for community-scale development.

Communities, from local associations to nation-scale institutions, should retain
the ability to choose and revise how they achieve these outcomes. Mainstay's
smaller protocol set is one approach to explore. Its value depends partly on
whether communities can adapt or replace it as their capabilities develop.

## Shared goals at a different starting scale

The World Bank treats a wallet as part of an ecosystem of issuers, holders,
verifiers, operators, and governance arrangements. It explicitly supports chip
cards, cloud wallets, and paper alternatives for people without smartphones
or suitable connectivity (printed pp. 4 and 22).

Mainstay begins with a community's actual relationships and responsibilities.
A cooperative, clinic, municipality, or association can identify the services
people need, recognize the responsible actors, and establish appropriate
operating rules. Connections to wider institutions can be added for the
activities that need them.

This applies the principle in [Clarity of Priority](clarity-of-priority.md):
community purpose leads, while applicable obligations shape responsible
operation. Local capability and cooperation with government can develop
together.

## Preserve institutional and technological choice

The World Bank's framework leaves room for different implementations. That
flexibility should extend to the assumptions beneath a wallet project: where
authority originates, what kinds of records matter, how people participate,
and which parts of the system must share a common trust arrangement.

A community needs concrete technical choices to begin operating. It should
make those choices with a defined purpose and a practical path to revision.
Choosing a protocol for today's service should not determine every future
institutional relationship or require every record to follow the same model.

Several questions help preserve that freedom:

- Can recognized local relationships support useful exchange before a wider
  institutional framework is complete?
- Can existing records acquire verifiable evidence without first being
  converted into one credential format?
- Can people participate fully through a card or assisted service, with a
  phone as one available interface?
- Can communities exchange evidence while retaining different recognition
  policies and responsibilities?
- Can cooperation grow through independently operable services, including
  within a national program?

These questions apply to Mainstay as much as to any national wallet proposal.
A smaller protocol set may reduce the number of mechanisms needed to begin,
but it must still support documented interfaces, exportable evidence, independent
verification, and replacement. Fewer protocols are useful when they reduce
the burden on people and operators without closing off future capabilities.

### Leave room for institutions to develop

We do not yet know the full range of institutional capabilities this
infrastructure may enable or restore. Communities may recover familiar
functions such as keeping authoritative records, witnessing agreements,
administering shared resources, and maintaining reciprocal obligations. They
may also develop new ways to cooperate across distance and organizational
boundaries.

The design should leave room to examine inherited administrative arrangements,
including those established during the twentieth century, alongside assumptions
carried into early twenty-first-century digital services. Their continued use
should follow from present needs and accountable decisions. Digitization is an
opportunity to reconsider how a responsibility is fulfilled, while preserving
the rights, safeguards, and institutional knowledge that make it legitimate.

### Build security into records and actions

Mainstay's architectural direction is to protect content, bind statements to
signing keys, constrain actions through explicit authorization, and preserve
verifiable evidence from the outset. A record's integrity and attributable
history should remain checkable as it moves between applications and networks.

This allows communities to benefit from the reach of browsers, existing
networks, and established services while retaining a trust model they can
govern. Secure transport remains essential; evidence-level protection adds
continuity beyond a particular connection or website. Endpoints, custody,
recovery, and access controls still require careful security engineering.

The aim is to use existing network effects without making a particular host,
certificate hierarchy, platform, or transport the permanent source of authority
over community records. Early implementation choices should enable learning
and cooperation while leaving later institutional choices open.

## A common foundation for many kinds of records

The report already includes health and other sectoral credentials. Mainstay's
proposed extension concerns how records are represented and checked: preserve
the exact artifact and attach verifiable evidence about it, without requiring
every document to be converted into a new credential format first.

A lab report, council resolution, permit, inspection photograph, membership
record, or structured credential can all need answers to similar questions:
Is this the expected file? Who made a statement about it? Has that statement
been corrected or withdrawn? Is the signer recognized for this purpose?

OpenETR separates the artifact from signed evidence concerning it. Defined
rules derive consequential state from the evidence; a community or institution
then decides what to recognize and what effect to give it. A health service
still needs clinical meaning and appropriate authority. A public registry still
needs its own procedures. The reusable foundation supports those responsibilities
across file formats.

Safebox Web provides record storage, sharing, presentation, and selected
verification workflows through Acorn. OakGate provides managed access and
card-facing workflows around the same wallet foundation. These applications
can make a broader record model usable in ordinary service delivery.

## Simpler foundations with purposeful interoperability

The proposed simplicity comes from reusing exact-content digests, public-key
signatures, encrypted storage, signed events, and explicit verification rules.
OpenETR and the family's open protocols give those mechanisms a common form.
Specialized credential and domain standards can be supported where a partner
or service requires them.

This is a smaller common implementation core, not a claim that all standards
or domain agreements disappear. OpenETR is an evolving open specification;
its independent implementation base and assurance need continued development.
Interoperability with a national wallet scheme still requires that scheme's
formats, protocols, and recognition arrangements.

The opportunity is to use one evidence approach across many records, while
preserving native formats and adding adapters for specific relationships.
Simplicity should be judged by the work required to operate, verify, recover,
and replace the system.

## Separate secure access from authority over records

Communities do not inherently need a certificate authority to decide whom they
trust to issue or attest to local records. They can establish recognized public
keys, define each actor's scope, document appointments and delegations, and
maintain procedures for withdrawal, key replacement, and disputes.

Traditional CA-based WebPKI remains useful for HTTPS browser access and secure
application infrastructure. Its role is distinct from deciding whether a clinic
may attest to a health record or a clerk may publish a council resolution.

OpenETR supports this separation by making signed evidence inspectable and
state derivable under identified rules. The community supplies the recognition
policy. A valid signature shows attribution to a key; acceptance of the signer
and statement remains a separate decision.

Independent trust therefore requires dependable governance of keys and roles.
It does not mean accepting any self-published key. Wider recognition can use
formal certificates or other arrangements where appropriate without making
them the compulsory origin of every local relationship.

## A fully empowered card as a service access goal

Mainstay's inclusion goal should be explicit: **an NFC card, together with
accessible readers and supporting services, should substitute fully for a
personally owned phone in the community workflows offered to members.**

That means more than identifying someone at a counter. A person should be able
to receive and present records, use supported funds or credits, obtain help,
and recover access without borrowing another person's identity or maintaining
a private smartphone. Someone sharing a household phone should retain their
own account and authority.

OakGate already documents card-based payment, receipt of funds, record receipt,
record presentation, and separately enrolled sign-in. Its card points to a
custodial Acorn; records, funds, and the user's private key are held off-card.
Safebox Web documents card issuance and PIN-gated login, while its dedicated
card record-retrieval and sharing design remains a proposal. Full parity across
all tasks, devices, and recovery situations remains a delivery and testing goal.

The current low-cost cards are copyable memory tags. They depend on service-side
controls and do not provide the assurance of a cryptographic smart card.
OakGate's current payment and record flows do not require a PIN, while enrolled
login has a separate PIN policy. Sensitive workflows therefore need appropriate
authorization and terminal safeguards before their use is expanded.

Phone-free access still uses a reader, screen, power, and supporting services.
Community terminals or a staff member's device can provide these, with accessible
assistance and private interactions. Shared-device sessions should end cleanly,
and card loss should have a practical suspension and replacement process.

## Resilience through people and infrastructure

Removing dependence on a personal phone addresses device loss, affordability,
battery failure, and sharing. Local operation can also reduce dependence on
distant services, provided the required authentication, records, evidence,
storage, and authorization services are available locally.

These are distinct forms of resilience. Current OakGate card operations require
connectivity to supporting services. They should not be described as offline
card transactions. Checking a retained signature during an outage also does
not establish that no later correction or withdrawal exists.

Communities should test recovery, evidence freshness, provider replacement,
and assisted access alongside normal use. Continuity includes trained people,
funding, and clear procedures as well as software.

## A practical next step

A useful pilot would pair a community service desk with an independent verifier
and test both phone and card journeys using non-sensitive sample records.
It should demonstrate successful receipt and presentation, inspection of signed
evidence, local recognition decisions, lost-card replacement, shared-device
privacy, and honest behavior when services or evidence are unavailable.

The policy ambition is equal participation through simpler, reusable record
infrastructure that preserves communities' ability to choose and evolve.
The World Bank's implementation discipline gives that ambition
a constructive test: show that the whole service works for the people who need
it, including those who do not own a phone.

[Read the detailed analysis](https://github.com/trbouma/mainstay/blob/main/docs/WORLD-BANK-DIGITAL-WALLETS-COMMUNITY-RECORDS-ANALYSIS.md){ .md-button .md-button--primary }

## Reference and implementation evidence

Tullis, Christopher; Black, David; and Cooper, Adam. 2026. *Digital Wallets:
Implementation — Practical Guidance for Deploying Wallets at National Scale*.
Digital Wallet Policy Note Series, No. 3. © World Bank. Relevant printed pages:
3–4, 12–14, 20–22, 25–28, 34–42, 64–65, and 67–74.

The detailed analysis maps these passages to current product documentation,
implementation limits, and proposed acceptance checks. See also
[OpenETR's model](https://docs.openetr.org/),
[OakGate's card capabilities](https://github.com/trbouma/oakgate/blob/main/docs/card-capabilities-policy-brief.md),
and [Safebox Web's card design](https://github.com/trbouma/safebox-web/blob/main/website/nfc-card-design.md).
