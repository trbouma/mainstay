# Digital Public Infrastructure in Europe: Analysis Note

Status: source analysis  
Analysis date: 2026-09-17

## Source

Nicholas Gates, with Chloe Teevan, Emrys Schoemaker, Krisstina Rao, and
Federico Plantera, *Digital Public Infrastructure in Europe: How the European
Union (EU) Can Build the Capability to Deliver on Its Digital Sovereignty
Agenda*, OpenForum Europe, with support from Co-Develop, 2026, 39 pages.

The paper draws on a workshop held in Brussels on 21-22 April 2026 with more
than 50 participants from EU institutions, Member State governments,
international organizations, civil society, academia, and the open-source
community. Workshop observations are generally reported under the Chatham
House Rule. This note distinguishes the paper's argument from implications
drawn here for Mainstay.

## Executive assessment

The paper's strongest contribution is its reframing of digital sovereignty as
an operational capability rather than primarily a regulatory condition. Europe
does not become sovereign merely by constraining vendors, localizing data, or
substituting a European supplier for a foreign one. It gains meaningful agency
when public institutions can build, operate, maintain, adapt, connect, and, if
necessary, replace foundational digital components without rebuilding every
service above them.

The paper uses Digital Public Infrastructure (DPI) to organize this argument.
Its core domains are identity, payments, and trusted data exchange, with
communications infrastructure identified as a possible fourth. Europe already
possesses important implementations in each domain. Its deficit is the
connective institutional capability that makes those implementations visible,
interoperable, reusable, sustainably funded, and governable across Member
States.

The prescription is intentionally incremental. The authors do not call for one
centralized European stack or another comprehensive strategy. They propose
using existing institutions, standards, funding vehicles, procurement rules,
and national implementations to develop a shared capability to deliver. This
approach is persuasive because it fits the EU's actual constitutional and
administrative structure: Member States retain operational responsibility,
while European institutions establish common rules, trust relationships, and
mechanisms for mutual recognition.

For Mainstay, the most important lessons are architectural rather than
geographic. Durable identity should remain distinct from network location;
governance frameworks should remain distinct from particular products;
foundational components should be substitutable; and local operational
capability should cooperate through explicit recognition and interoperability
rules. Mainstay can embody these properties at community and institutional
scale. It should not claim that a deployment automatically constitutes
population-scale DPI or acquires public authority by technical design.

## The paper's central argument

The argument proceeds in five steps.

1. Europe has substantial digital dependency in foundational systems.
2. Regulation and investment have produced rules and individual assets, but
   not a coherent operational layer connecting them.
3. DPI provides a useful frame for shared, secure, interoperable foundations
   built on open standards.
4. Europe already operates many DPI-like systems; the problem is weak
   visibility, coordination, maintenance, reuse, and delivery capacity.
5. European digital sovereignty therefore requires a capability to deliver:
   the continuing institutional ability to build, operate, change, and sustain
   foundational infrastructure.

This moves the sovereignty question from provenance to agency. A European-made
component can still create dependency if it is difficult to replace. Conversely,
a system assembled from multiple sources can preserve agency when its
interfaces, governance, skills, and operations keep substitution practical.

The paper expresses this through a particularly useful practical test:

> Can a component be changed or replaced without rebuilding what sits above it?

This **substitutability test** is more demanding than vendor nationality,
open-source licensing, or data residency alone. It evaluates whether an
institution retains the capacity to move.

## What the paper means by DPI

The paper adopts the G20 conception of DPI as shared digital systems that are
secure, interoperable, and based on open standards, providing population-scale
access to essential public and private services. It highlights three commonly
recognized layers:

- digital identity;
- digital payments; and
- trusted data exchange.

The workshop also identifies communications as a possible fourth capability.

The authors distinguish DPI from a vertically controlled platform. A platform
typically aggregates users and services inside an operator's ecosystem. DPI
uses minimal common systems, protocols, and trust frameworks so that multiple
public and private actors can build above them without one actor controlling
the entire environment.

DPI is not inherently synonymous with open-source software. Open licensing can
improve inspectability, reuse, contribution, and substitutability, but the paper
treats technology, governance, and adoption as three separate and necessary
dimensions. Public control over the foundation does not require public control
over every application built on it.

## Europe already has many of the pieces

The paper rejects the premise that Europe must invent DPI from scratch. It
identifies working national and European initiatives, including:

- FranceConnect for federated identity;
- Spain's Cl@ve and Italy's SPID for identity;
- Italy's PagoPA for payments;
- Estonia's X-Road for data exchange;
- Denmark's MitID and Digital Post;
- the EU Digital Identity Wallet and eIDAS 2.0 trust framework;
- the proposed digital euro;
- Common European Data Spaces;
- La Suite Numérique and openDesk; and
- GovStack specifications.

These examples reveal a structural asymmetry. A Member State can build and run
a coherent system within its own institutions, but may lack continental scale.
The EU can set rules at continental scale, but normally does not operate the
underlying systems. The opportunity lies in connecting national delivery with
European coordination rather than forcing either level to replace the other.

The paper presents eIDAS 2.0 as the clearest example. Member States retain
responsibility for issuing and managing credentials; a common governance layer
defines how credentials are recognized across borders. The significant
artifact is not only the wallet application. It is the architecture of rules,
standards, roles, and trust relationships.

## Regulation is necessary but insufficient

The paper respects the EU's regulatory strength but argues that rulemaking does
not itself create operational capacity. Adding rules does not build a system;
removing rules does not build one either. Institutions need authority, staff,
funding, procurement competence, technical skills, operational responsibility,
and permission to experiment.

The authors distinguish two approaches:

| Approach | Primary concern | Limitation when used alone |
| --- | --- | --- |
| Structural exposure reduction | Reduce reliance through procurement rules, localization, European preference, and vendor diversification | Can relocate dependency without making systems easier to change or operate |
| Capability building | Develop the ability to build, maintain, adapt, extend, and replace infrastructure | Requires sustained institutions, skills, funding, and operational accountability |

The approaches complement one another. Exposure matters, but sovereignty is
thin when a public institution cannot operate or replace the compliant system
it procures.

The EU Digital Identity Wallet illustrates this problem. Member States can
issue wallets under European rules, yet smartphone secure elements, device
attestation, and application distribution remain controlled largely by Apple
and Google. The EU can govern the credential layer while inheriting terms at
the device and distribution layers.

## Build on and connect what exists

The paper repeatedly advises against a new monolithic European stack. Its
preferred approach is to:

- recognize existing implementations as a shared class of infrastructure;
- fund maintenance, not only new development and pilots;
- publish reusable reference implementations;
- align procurement with open standards and interoperability;
- create common specifications and trust frameworks;
- support knowledge exchange among delivery teams;
- strengthen internal public-sector delivery units; and
- coordinate existing national systems without replacing them.

This is a federated model. Shared rules make cooperation possible while Member
States retain operational and constitutional autonomy. It fits the paper's
broader claim that Europe needs connective tissue more than another strategy.

## Proposed institutional vehicles

The paper identifies several existing or proposed mechanisms.

### DPI Steward Organisation

The proposed steward would add value only with a concrete delivery mandate and
budget. Its functions would include:

- maintaining a register of European DPI capabilities;
- coordinating and sustaining existing implementations;
- supporting technical development;
- maintaining shared specifications;
- sharing knowledge and funding; and
- acting as a point of contact across relevant Commission directorates,
  external-action institutions, and Member State agencies.

The paper warns implicitly against creating another coordination body without
authority to deliver.

### Digital Commons EDIC

The Digital Commons European Digital Infrastructure Consortium is presented as
the most practical near-term vehicle. Its intergovernmental structure enables
participating Member States to collaborate on open digital infrastructure
without waiting for full EU harmonization.

### Existing policy and funding instruments

The paper also points to:

- the Interoperable Europe Act as governance connective tissue;
- revised Public Procurement Directives as a route to make open standards,
  interoperability, and substitutability procurement criteria;
- the European Competitiveness Fund as a potential investment vehicle;
- the EU Open Source Strategy;
- the Open Internet Stack initiative; and
- GovStack specifications as reusable implementation guidance.

Its institutional strategy is pragmatic: connect and redirect instruments that
already exist instead of waiting for a complete new regime.

## Internal recommendations

The detailed recommendations can be condensed into six operating priorities:

1. **Fund DPI as maintained infrastructure.** Dedicate funding to adoption,
   pilots, integration, maintenance, and shared capacity, not only invention.
2. **Give stewardship a delivery mandate.** Resource the steward and Digital
   Commons EDIC to perform work that currently has no owner.
3. **Procure for substitutability.** Treat open standards and interoperability
   as sovereignty and industrial-policy criteria.
4. **Publish reusable implementations.** Release reference implementations
   under open licences together with governance documentation.
5. **Build public delivery capacity.** Establish or strengthen internal teams
   and reduce dependence on consultants for foundational systems.
6. **Coordinate across levels.** Nominate points of contact and create durable
   collaboration among European and national institutions.

## From external funder to reciprocal partner

The paper's external-policy argument follows from its domestic diagnosis. The
EU often appears in global DPI work as a funder and norm-setter rather than an
implementer. Because European implementations are poorly catalogued and not
presented as a coherent portfolio, Europe brings financing and rules to
partnerships more readily than operational practice.

The authors propose a **Brussels Partnership** in place of a one-directional
Brussels Effect. The distinction is between exporting finished regulatory
frameworks and co-developing standards, specifications, and governance with
partners whose contexts differ.

This requires:

- mapping European implementations and registering them in global catalogues;
- sending practitioners, not only funders and diplomats, to DPI fora;
- creating feedback channels from international work into domestic policy;
- learning from India, Brazil, Ukraine, Estonia, Norway, and Global South
  implementations;
- coordinating development agencies through a shared DPI frame;
- funding maintenance of digital public goods on which systems depend; and
- analysing actual investment and institutional absorption capacity before
  creating new financial instruments.

The paper is particularly effective in recognizing that standards designed for
high-capacity European institutions can constrain partners when attached to
capital or market access. Reciprocity requires adaptation and co-development,
not nominal consultation around a finished European design.

## Strengths of the paper

### It makes sovereignty testable

The substitutability test turns a broad political term into an architectural
and procurement question. It exposes dependencies that nationality or licensing
labels can obscure.

### It centers maintenance and operations

The paper treats funding, staffing, maintenance, and institutional ownership as
part of infrastructure. This corrects a common bias toward launches, pilots,
and legislative frameworks.

### It fits a plural constitutional order

The model does not require the EU to behave like a unitary state. Mutual
recognition, common trust frameworks, and federated implementation align with
the continued authority of Member States.

### It connects domestic capacity and international credibility

The claim that a credible external offer begins with practiced domestic
capability is compelling. Institutions learn differently when they operate the
systems about which they advise others.

### It avoids equating DPI with one product or licensing model

The separation of technology, governance, and adoption keeps the analysis from
collapsing DPI into an application catalogue or an open-source policy alone.

## Limitations and open questions

### Evidence base

The paper is a policy argument informed substantially by one expert workshop.
It does not present comparative cost analysis, adoption data, or outcome
evaluation sufficient to establish which institutional mechanism will work
best. Several recent proposals were still developing when written.

### Definition remains intentionally loose

The paper benefits from avoiding a rigid DPI definition, but the same
flexibility can blur the boundary among public infrastructure, digital public
goods, shared government platforms, and ordinary interoperable services. A
working portfolio still needs inclusion criteria.

### Safeguards are acknowledged more than developed

Surveillance, privacy, exclusion, smartphone dependence, and safeguards appear
throughout the paper, but they are not developed into a complete accountability
framework. Population-scale identity and payment systems concentrate real
power even when technically federated.

### Political legitimacy requires more attention

The paper is strongest on institutions and delivery teams. It says less about
how citizens, affected communities, parliaments, independent regulators, and
civil society participate in defining acceptable infrastructure and remedies.

### Sustainability needs an operating model

The authors correctly emphasize maintenance but do not fully specify how
long-term costs, liabilities, shared ownership, service levels, incident
response, and exit obligations would be allocated across the EU and Member
States.

### Open source is helpful but not sufficient

Publishing code does not create a maintainer community, deployment competence,
secure supply chain, or ability to fork. Reference implementations require
documentation, governance, testing, funded maintenance, and users with the
capacity to operate them.

### Inclusion cannot be an application-layer afterthought

The smartphone critique points to a wider issue: identity, payment, and record
systems need assisted, offline, delegated, accessible, and non-digital paths.
Otherwise, a technically interoperable foundation can reproduce exclusion.

## Implications for Mainstay

### Mainstay operates at a different scale

The paper defines DPI around population-scale essential services. Mainstay
starts with a community, organization, venue, or local institution. A Mainstay
deployment is not automatically DPI. It becomes relevant to a DPI ecosystem
when legitimate public or community authorities use it as a governed component
of shared infrastructure and connect it through recognized standards and trust
frameworks.

### The product family reflects DPI separation of concerns

Mainstay's component boundaries correspond to several concerns in the paper:

| DPI concern | Mainstay-family capability | Boundary |
| --- | --- | --- |
| Portable authority and identity | Acorn and signed keys | Does not confer legal identity or public authority |
| Payments and bounded exchange | Clear | Does not replace sovereign currency, banking, or universal acceptance |
| Records and data exchange | OpenETR, Grove, and Spurline | Storage and evidence do not determine legal recognition |
| Communications | Stroma and Spurline | A relay transports events but does not become their authority |
| Local coordination and operations | Mainstay and Lockbox | The application and appliance do not become the underlying institutions |

This is consistent with public control over foundations without central control
over every application or institution above them.

### Good boundaries enable substitutability

Mainstay's principle of **good boundaries, not barriers** can be evaluated with
the paper's substitutability test:

- Can a relay change without changing the identity of the service or record?
- Can storage move without changing the digest of the artifact?
- Can an application be replaced without losing keys, proofs, or evidence?
- Can an endpoint change without renaming the service?
- Can a local mint or record authority remain distinct from the wallet that
  presents its state?

Positive answers provide evidence of capability, not merely reduced exposure.

### Identity outlives location

The paper's concern about inherited infrastructure terms reinforces Mainstay's
separation of stable identity from replaceable routes. DNS names, cloud hosts,
container names, VPN paths, and local addresses are ways to reach a service;
they are not the service's durable identity. This makes movement possible
without rebuilding dependent applications.

### Recognition is a governance architecture

The treatment of eIDAS 2.0 as a governance architecture aligns with OpenETR's
separation of exact artifacts, signed evidence, consequential state, and
recognition. One community can attest to a record under its rules; another can
apply its own recognition policy. Interoperability does not require a central
authority to determine the meaning of every record.

### Local-first can contribute to delivery capacity

Mainstay provides a concrete environment in which services can be installed,
operated, observed, backed up, recovered, and connected. That operational
surface matters because protocol compatibility alone is not a capability to
deliver. A credible contribution also requires:

- stable service and health contracts;
- documented installation and recovery;
- pinned and reviewable component versions;
- security updates and incident procedures;
- operator training and accessible support;
- tested migration and component replacement;
- governance documentation alongside code; and
- sustainable maintenance arrangements.

### Cooperative independence parallels federated DPI

Mainstay's **cooperative independence** is compatible with the paper's European
model. Local authorities retain their own rules and operations while using
shared protocols and explicit recognition agreements to cooperate. Local-first
does not mean isolated, and interoperability does not require centralization.

## Proposed Mainstay policy position

Mainstay can adopt the following position:

1. Digital sovereignty is demonstrated by the ability to operate, understand,
   change, and replace foundational components.
2. Mainstay is community-scale infrastructure that can participate in wider
   DPI arrangements; it does not claim public authority by itself.
3. Stable identity, portable evidence, open protocols, and replaceable routes
   are design requirements for cooperative independence.
4. Clear, OpenETR, Grove, Spurline, Acorn, and Stroma retain separate authority
   and failure boundaries.
5. Reference implementations must include governance, installation, recovery,
   maintenance, and migration documentation.
6. Cross-community or cross-government operation depends on explicit trust and
   recognition frameworks, not technical connectivity alone.
7. Accessibility, privacy, assisted service, offline operation, appeal, and
   non-digital alternatives are infrastructure concerns.
8. Procurement and architecture reviews should apply the substitutability test
   to every foundational dependency.

## Questions for further work

1. What objective criteria distinguish a Mainstay deployment from a component
   of DPI?
2. Which service contracts and conformance tests make each component genuinely
   substitutable?
3. What governance package must accompany a reusable Mainstay reference
   implementation?
4. How can community-scale trust frameworks connect to municipal, provincial,
   national, Indigenous, and international recognition systems?
5. Which functions remain usable without a smartphone, continuous internet,
   or a single vendor's application-distribution channel?
6. What institution funds long-term maintenance and coordinates disclosure,
   incident response, and upgrades across the product family?
7. How are affected people represented in decisions about identity, payment,
   record, and data-exchange infrastructure?
8. What measurements demonstrate availability, portability, substitutability,
   inclusion, and successful recovery in practice?

## Conclusion

The paper offers a disciplined account of digital sovereignty: the decisive
question is not only where technology comes from or which rules apply, but
whether an institution retains the capability to deliver and change the
foundations on which it depends.

Europe's path is federated. Existing national implementations remain in place
while shared governance, recognition, investment, and interoperability make
them more than disconnected successes. The same principle can guide Mainstay
at a smaller scale. A community keeps meaningful local capability, preserves
clear authority boundaries, and cooperates with wider networks through open
protocols and explicit governance.

That is not a claim that Mainstay is already European DPI. It is a design and
operational standard: infrastructure becomes trustworthy when the people and
institutions responsible for it can understand, govern, sustain, connect, and
replace it.

