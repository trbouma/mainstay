---
title: Indigenous Community Stewardship in Canada
description: A Canadian policy frame for community-governed digital infrastructure, records, and bounded program value.
---

# Indigenous Community Stewardship in Canada

**Policy brief**

## Core proposition

Indigenous communities in Canada can operate digital infrastructure that
reflects their own laws, governance, languages, relationships, and service
realities while remaining connected to Canadian public institutions, financial
systems, and neighbouring communities.

Mainstay calls this **cooperative independence**. A community keeps practical
capability close enough to govern and use, without treating local operation as
isolation or as a substitute for the relationships, rights, treaties,
agreements, laws, and public services that continue to matter.

This brief considers how local-first infrastructure can support that work. It
also examines one bounded use of Clear: administering community-defined
benefits, allowances, vouchers, or service credits among willing participants.
Clear does not replace Canadian currency, cash, bank deposits, public benefits,
or the community's obligations to members and providers.

## There is no single Indigenous context

"Indigenous community" is not one legal or political category. Section 35 of
the *Constitution Act, 1982* recognizes and affirms existing Aboriginal and
treaty rights and identifies the Aboriginal peoples of Canada as the Indian,
Inuit, and Métis peoples of Canada. It also confirms that treaty rights include
rights arising from land claims agreements. The
[constitutional text](https://laws.justice.gc.ca/eng/Const/FullText.html#h-50)
is a necessary starting point, not a complete description of any Nation's
rights, laws, or relationships.

First Nations, Inuit, and Métis are distinct peoples. Within those broad terms
are many Nations, governments, communities, treaty relationships, settlement
areas, languages, laws, histories, and institutional forms. The Government of
Canada's own
[principles respecting its relationship with Indigenous peoples](https://justice.canada.ca/eng/csj-sjc/principles-principes.html)
recognize that a distinctions-based approach is needed to respect their unique
rights, interests, and circumstances.

A Mainstay deployment therefore begins with the community's actual governance,
not a generic Indigenous configuration. The responsible people must identify:

- which Nation, government, community, organization, or program is acting;
- the legal and community authority under which it acts;
- which citizens, members, residents, clients, or providers participate;
- which laws, treaties, agreements, funding terms, and policies apply;
- which language and accessibility needs shape the service; and
- which decisions remain with another Indigenous, federal, provincial,
  territorial, municipal, professional, or private institution.

Technology can express those decisions. It cannot make them on the
community's behalf.

## Self-determination is an operating principle

The federal *United Nations Declaration on the Rights of Indigenous Peoples
Act* affirms the Declaration as a universal international human-rights
instrument with application in Canadian law and provides a framework for the
Government of Canada's implementation of it. Its schedule includes rights
concerning self-determination, autonomy or self-government in internal and
local affairs, participation in decision-making, and the maintenance and
development of Indigenous institutions. The
[Act and scheduled Declaration](https://laws-lois.justice.gc.ca/eng/acts/U-2.2/)
provide a national policy context for community-led infrastructure; they do not
turn software into jurisdiction or settle how a particular provision applies
in a particular case.

For Mainstay, self-determination has practical consequences:

- the community defines the problem before selecting the technology;
- community authorities approve the rules and appoint operational roles;
- members can understand what the system does and how decisions are reviewed;
- outside vendors do not become the source of community authority;
- information and operational capability remain portable; and
- the deployment can cooperate with outside systems on documented terms.

Procurement alone is not self-determination. A community does not gain durable
control merely because a server is physically nearby or a vendor calls a
product sovereign. Keys, records, policies, administrative access, recovery
material, skills, contracts, and exit options all matter.

## Information governance comes before data hosting

Local infrastructure can help a community keep records available, protect
confidentiality, and reduce dependence on a remote vendor. Those are useful
capabilities, but data location by itself does not answer who owns information,
who controls its use, who can gain access, or who possesses the operational
copy.

For First Nations, the First Nations Information Governance Centre describes
the First Nations Principles of **OCAP®**—Ownership, Control, Access, and
Possession—as a framework for how First Nations data and information are
collected, protected, used, and shared. FNIGC stresses both that OCAP® is
expressed according to each Nation's worldview and protocols and that it is
specifically a First Nations framework, not a generic framework to be applied
to all Indigenous peoples. See FNIGC's
[authoritative introduction to OCAP®](https://fnigc.ca/ocap-training/).

OCAP® is a registered trademark of the First Nations Information Governance
Centre (FNIGC).

Inuit and Métis governments and organizations have their own governance
institutions, research ethics, data strategies, and community protocols. A
project must work from the applicable people's own authorities rather than
renaming a First Nations framework and treating it as universal.

A community-led Mainstay deployment can support information governance by
keeping encrypted records locally available, preserving verifiable evidence,
separating service operation from record authority, and allowing components to
be replaced without silently transferring control. It still requires policy
for:

- collection, purpose, consent, and lawful authority;
- individual privacy and collective interests;
- access, correction, retention, disclosure, and deletion;
- cultural knowledge and records requiring special protocols;
- secondary use, research, analytics, and artificial intelligence;
- incident response, audit, recovery, and breach notification; and
- transfers to governments, health systems, funders, professionals, courts,
  archives, or other relying institutions.

The community's law and policy give a record meaning. Mainstay, Grove,
Spurline, and OpenETR can preserve bytes, events, provenance, and derived state;
none of them decides that a record is culturally, administratively, or legally
authoritative.

## Local-first infrastructure for Canadian realities

Indigenous communities operate in urban, rural, remote, northern, coastal, and
road-accessible settings. Connectivity, power, staffing, travel, and vendor
support differ considerably among them. The CRTC continues to identify gaps in
underserved rural, remote, and Indigenous communities through its
[Broadband Fund](https://crtc.gc.ca/eng/internet/fnd/index.htm). Local-first
design treats an unstable outside connection as an ordinary operating
condition without assuming that every community faces the same constraint.

A local Mainstay instance can keep selected services available on a community
network, then synchronize or reconcile with wider systems when an eligible
route returns. That can improve continuity for records, approvals, program
administration, and bounded value. It does not make a disconnected local copy
authoritative for every outside purpose, and it does not remove the need for
tested backups, cybersecurity controls, skilled operators, accessible support,
and manual fallbacks.

Language is equally operational. A community can choose its public name,
service terminology, preferred language, and approved translations without
changing cryptographic identifiers or protected security messages. Translation
must be reviewed in context by speakers chosen by the community; a software
locale or machine translation is not evidence of cultural or linguistic
fitness.

## Using Clear to administer a defined program

A community government or organization may need to distribute a benefit for a
specific purpose: food, transport, fuel, accommodation, school supplies,
cultural programming, recreation, local services, emergency support, or an
approved internal allocation. Conventional options—including cash, cheques,
direct deposit, prepaid cards, reimbursements, and provider invoicing—may
remain appropriate. Clear adds another option for a deliberately bounded
program.

Clear issues private bearer **Mint Notes** denominated in an issuer-defined
Clear Mint Unit. The community can define what one unit represents, who may
authorize issuance, which providers voluntarily accept it, how providers are
settled, when units expire if expiry is appropriate, and what happens when a
member loses access or disputes a transaction.

A possible lifecycle is:

```text
approved program budget
    -> authorized allocation
    -> Mint Notes delivered to participant
    -> participant transfers notes to an accepting provider
    -> provider validates and redeems notes
    -> program clears the claim and settles with the provider
    -> redeemed notes are retired and aggregate accounts reconciled
```

This separates several responsibilities that are often blurred together:

- **eligibility** determines who qualifies under the program;
- **authorization** approves a particular allocation;
- **issuance** creates the corresponding Mint Notes;
- **acceptance** is the provider's voluntary agreement to take them;
- **transfer** moves bearer proofs from the participant to the provider;
- **clearing** validates and accounts for the returned claim;
- **settlement** fulfils the issuer's promise to the provider; and
- **reporting** accounts for the program without exposing every participant's
  complete transaction history.

The community remains responsible for the program. Clear supplies issuance,
transfer, validation, redemption, retirement, and supply evidence. It does not
decide eligibility, create a budget, fund the issuer's obligations, guarantee
provider settlement, or resolve conflicts among governing authorities.

## Clear is not a substitute for cash

A Clear Mint Unit is not a Canadian dollar merely because its display label or
program accounting uses a dollar-like amount. It is not a Bank of Canada note,
a Royal Canadian Mint coin, a bank deposit, or legal tender. The
[Bank of Canada explains](https://www.bankofcanada.ca/2021/01/about-legal-tender/)
that bank notes and eligible coins are Canada's legal tender, while parties may
agree to other forms of payment. Agreement does not make the alternative form
legal tender or require anyone else to accept it.

Clear therefore works best when the interface and policy state plainly:

- the full name of the issuing community or organization;
- what the unit represents and what obligation stands behind it;
- that acceptance is voluntary and limited to identified participants;
- where and for what the unit can be used;
- whether transfer between participants is permitted;
- how redemption, provider settlement, expiry, refunds, and disputes work;
- whether and on what terms a holder can receive Canadian dollars; and
- whom to contact when the instrument cannot be used as expected.

Community members must retain meaningful access to Canadian-dollar funds and
ordinary payment options when the underlying benefit, agreement, funding
condition, accessibility need, or law requires them. A program must not label a
restricted digital credit as "cash," quietly convert wages or unrestricted
funds into it, or make essential services conditional on owning a compatible
phone. Paper, card, assisted, or conventional alternatives may be necessary.

The distinction protects both members and the community treasury. Clear can
help administer an obligation; it cannot make an underfunded promise whole.

## Privacy with accountable public administration

Blind-signed Mint Notes can reduce routine disclosure of who paid whom. That
privacy can be valuable in a small community where a conventional named-account
ledger may reveal sensitive patterns. It is not complete anonymity: devices,
networks, issuance, redemption, provider activity, and surrounding program
records can still reveal information.

Good administration does not require publishing every participant's purchases.
It does require evidence that authorized people issued within an approved
budget, total supply is reconciled, redeemed claims are retired, providers are
settled correctly, exceptions are reviewed, and misuse can be investigated
under a known process.

The practical design goal is **private participation with accountable
authority**:

- minimize personal information at transfer time;
- separate eligibility records from bearer-payment events where feasible;
- publish program rules before issuance;
- require multiple approvals for consequential treasury actions;
- record aggregate issuance, redemption, outstanding liability, and settlement;
- limit exceptional tracing or disclosure to documented authority; and
- give participants accessible correction, complaint, and appeal routes.

## Canadian legal and regulatory review remains necessary

The legal treatment of a program depends on its facts: the issuer, unit,
participants, convertibility, transferability, funding source, geographic
reach, and services being provided. A closed community benefit and an openly
traded, Canadian-dollar-redeemable instrument do not present the same issues.

Before live issuance, the responsible authority should obtain advice on the
laws and agreements that actually apply, including Indigenous law, treaty and
self-government arrangements, program and contribution agreements, tax,
employment standards, consumer protection, privacy, unclaimed property,
financial administration, and anti-money-laundering obligations.

Two federal regimes illustrate why the operating model matters:

- FINTRAC states that businesses engaged in remitting or transmitting funds or
  dealing in virtual currency may be money services businesses with
  registration, compliance, identification, recordkeeping, and reporting
  obligations. Its current
  [money-services-business guidance](https://fintrac-canafe.canada.ca/msb-esm/msb-eng)
  requires analysis of the actual service rather than its product name.
- The Bank of Canada's guidance under the *Retail Payment Activities Act*
  applies a functional test to payment service providers and also identifies
  exclusions, including some internal and closed-loop transactions. See the
  Bank's
  [registration criteria](https://www.bankofcanada.ca/2026/06/criteria-for-registering-payment-service-providers/).

These references do not determine whether a particular community program is in
scope or exempt. "Local," "non-profit," "community-issued," or "not cash" is
not by itself a legal conclusion. The community should document its analysis
and review it when the program changes.

## A community decision framework

Before deploying Mainstay or issuing with Clear, a community can ask:

1. What community-defined need are we solving, and who asked for it?
2. Which Nation, government, organization, or program has authority to act?
3. How are First Nations, Inuit, or Métis distinctions reflected rather than
   collapsed into a generic model?
4. Which community laws, protocols, languages, and accessibility requirements
   govern the work?
5. What information is collected, and who owns, controls, accesses, possesses,
   retains, and can disclose it?
6. What does each Clear unit represent, and what funded obligation stands
   behind it?
7. Is acceptance voluntary, and can members still use cash or ordinary payment
   channels where appropriate?
8. How are providers enrolled, validated, settled, and given recourse?
9. What happens after device loss, key loss, fraud, an outage, a disputed
   purchase, expiry, or program closure?
10. Which legal, regulatory, tax, funding, and audit requirements apply?
11. Can the community recover the system and move to another operator or
    product without losing identities, records, balances, or evidence?
12. How will citizens and members evaluate the program and change or end it?

The answers belong in community-approved policy, training, agreements, and
operational procedures—not only in software configuration.

## Mainstay's role

Mainstay coordinates a locally operated environment without becoming the
community's government, archive, treasury, or source of jurisdiction:

- Mainstay supplies installation, service coordination, status, and recovery;
- Safebox Web gives participants access to records and wallet functions;
- Acorn preserves portable keys, records, and Mint Notes;
- Clear supports bounded issuance, transfer, redemption, and retirement;
- Grove stores encrypted, content-addressed artifacts;
- Spurline carries signed events across eligible local and wider routes;
- Stroma supplies narrow Nostr protocol operations; and
- OpenETR can preserve evidence and derived state for exact Digital Artifacts.

The components provide capability. The community supplies authority, meaning,
policy, people, funding, accountability, and care.

## Conclusion

Indigenous-led digital infrastructure in Canada begins with the rights,
governance, and practical circumstances of the particular people and community.
It is not achieved by applying one technical sovereignty label across First
Nations, Inuit, and Métis contexts.

Mainstay can give community-defined records, services, and operational
capabilities a dependable local home. Clear can help a community disburse and
account for a specific funded benefit among willing participants and providers.
That is a useful but deliberately limited role: Clear is a tool for administering
a defined obligation, not a replacement for Canadian currency, cash access,
banks, public benefits, or community governance.

The measure of success is not how much activity the software captures. It is
whether the community retains understandable authority, participants are
treated fairly, obligations are honoured, information is governed properly,
and cooperation with the wider systems people rely on remains dependable.

