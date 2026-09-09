---
title: Credit, Clearing, and Transferring Value
description: How communities can use modern cryptography to support the ancient social practices of credit, transfer, clearing, and settlement.
---

# Credit, Clearing, and Transferring Value

**Policy brief**

## Core proposition

Credit is older than coinage, paper notes, and modern banking. Long before
people carried standardized currency, they lived within relationships of
obligation, contribution, entitlement, trust, and return.

Mainstay does not propose replacing those relationships with a new digital
currency. It asks how communities and institutions can support the familiar
work of extending credit, transferring claims, clearing obligations, and
settling accounts with better privacy, clearer authority, portable evidence,
and dependable local availability.

The technology is new. The social function is ancient.

## Credit before currency

A familiar story says that early people began with barter, found direct swaps
inconvenient, invented money, and only later developed credit. In
[*Debt: The First 5,000 Years*](https://davidgraeber.org/books/debt-the-first-5000-years/),
anthropologist David Graeber challenged that sequence.

His argument was not that barter never occurs or that every society organizes
value in the same way. It was that there is little evidence for a generalized
barter economy as the original condition from which money naturally emerged.
Everyday economic life usually took place inside continuing relationships.
People contributed, received, remembered, promised, reciprocated, allocated,
and kept accounts because they expected to deal with one another again.

In Graeber's account, the more useful starting question is how a broad social
sense of obligation, an "I owe you one," became measurable as a unit of
account. By the time written records appear in ancient Mesopotamia, elaborate
accounting and credit arrangements are already present. Standardized coinage
came much later. Graeber therefore describes history not as one straight line
from barter to cash to credit, but as recurring periods in which credit,
account money, coin, and bullion take different roles. He also stresses that
economic life has always mixed several principles, including reciprocity,
allocation, hierarchy, gift, obligation, and exchange. See his
[2011 interview on debt and the barter narrative](https://davidgraeber.org/interviews/what-is-debt-interview-with-david-graeber/)
and essay on the
[history of virtual money](https://davidgraeber.org/articles/debt-the-first-five-thousand-years/).

This is a valuable cultural frame for Mainstay. Credit is not merely a bank
product or a score assigned by a distant platform. At its root, it is a
recognized relationship: someone has provided, promised, earned, allocated, or
become entitled to something, and a community has a way to remember what
follows.

## Credit is a relationship

A credit has two sides:

```text
holder's claim <-> issuer's obligation
```

The holder can present or transfer the claim. The issuer, treasury, or
participating provider recognizes an obligation under defined terms. Those
terms might promise money, food, accommodation, transport, an hour of service,
access to a shared resource, or an internal accounting treatment.

The instrument does not create the relationship by itself. A coin, note,
ledger entry, voucher, or digital proof makes the relationship easier to
identify and use. Its meaning still comes from the people and institutions
that issue, accept, redeem, and govern it.

This is why Mainstay treats authority and recognition as visible parts of the
system. A technically valid instrument may still be outside its intended
network, expired under its policy, issued without proper authority, or
unrecognized by a proposed recipient. Cryptography can make evidence clearer;
it cannot make an unfair promise fair or require another person to accept it.

## Transfer and clearing are different

**Transfer** moves a claim from one holder to another. **Clearing** validates
and reconciles the transaction and establishes what remains to be settled.
**Settlement** discharges the obligation through the transfer of money, goods,
services, securities, or another agreed form of value.

This follows the conventional payments distinction. The
[European Central Bank's glossary](https://www.ecb.europa.eu/services/glossary/html/act7c.en.html)
defines clearing as reconciliation and possible confirmation before settlement,
including establishment of the positions to be settled. Community instruments
may have different settlement assets and procedures, but the distinction is
still useful.

```text
issue -> hold -> transfer -> present -> validate and clear -> settle -> retire
```

Clearing may involve:

- identifying the issuer and exact unit;
- validating that the instrument is authentic and has not already been spent;
- matching presentations, returns, and treasury records;
- confirming the obligation or allocation to be discharged;
- calculating any position owed to a participating provider; and
- preserving enough evidence to reconcile supply and obligations before
  settlement.

Settlement then fulfills the recognized obligation under the issuer's policy.
The issuer may deliver a good or service, reimburse a provider, make an
accounting entry, transfer another asset, renew the claim, or perform another
agreed act. Retiring a redeemed Mint Note prevents that bearer proof from
circulating again; it is evidence in the clearing lifecycle, not by itself a
guarantee that every real-world obligation was fulfilled.

The distinction matters. Passing a meal credit to another person transfers the
instrument. A participating kitchen validating and returning it lets the
program clear the transaction. Providing the meal and completing any promised
provider reimbursement settle the relevant obligations. The transfer can be
private and direct while clearing and settlement remain accountable to the
organization that made the promise.

## The Treasury function

Mainstay uses **Treasury function** for the enduring institutional capability
to define, authorize, account for, transfer, redeem, and settle value. It is a
function, not a required office or governance template.

A community exercising this function must be able to answer:

- What unit or claim is being used?
- Who has authority to issue it?
- What obligation, resource, or policy stands behind it?
- Who can hold and transfer it?
- Where is it voluntarily accepted?
- How is it redeemed, cleared, settled, or retired?
- What evidence allows the resulting accounts to be reconciled?

The related **Clerk function** preserves the consequential records behind
those answers: policies, appointments, budgets, eligibility decisions,
authorizations, receipts, and evidence that obligations were fulfilled. The
functions cooperate without becoming one authority. A record may authorize a
treasury action, but a document store does not thereby become a mint. A payment
application may transfer an instrument, but it does not become the sole source
of the agreement behind it.

[Read the Clerk and Treasury Functions brief](clerk-and-treasury-functions.md)
for the broader institutional model.

## Clear: an old function with new tools

Clear applies this model to bounded, organization-issued value. **Clear means
Credit-Liability Ecash: Authorized and Redeemable.** Each Clear Mint Unit is a
specific issuer-defined unit bound to its own keyset and policy. Its Mint Notes
are private bearer instruments that can move between compatible wallets
without maintaining a named account balance for every holder.

The organization still supplies the meaning:

- a community program may issue food or transport credits;
- a resort may issue guest, meal, activity, or staff allowances;
- a co-working facility may issue desk, room, printing, or event credits;
- a cooperative may allocate member benefits or service units; and
- an institution may represent an approved internal budget or entitlement.

Clear supplies issuance controls, blind signatures, bearer proofs,
double-spend protection, transfer, redemption, retirement, and supply evidence.
It does not decide whether the underlying program is legitimate, appoint its
treasurer, define the issuer's promise, or guarantee that promised goods and
services will be delivered.

The detailed Clear model is described in
[Why Clear?](https://trbouma.github.io/clear/why-clear/) and
[Old Function, New Tools](https://trbouma.github.io/clear/old-function-new-tools/).

Each instrument remains bounded. A resort meal credit is not national money. A
community transport credit is not automatically accepted by another program.
Two units do not become interchangeable merely because both use Clear. Their
usefulness comes from a legible relationship among issuer, holder, accepting
providers, policy, and clearing process.

## What cryptography changes

Ancient and traditional credit systems often relied on memory, witnesses,
marks, tallies, tablets, account books, trusted intermediaries, and continuing
relationships. Modern cryptography and digital communication add useful
affordances without eliminating the underlying social structure.

They can provide:

- signatures that make authorization independently verifiable;
- stable public-key identifiers for issuers, treasurers, services, and holders;
- blind signatures that improve transactional privacy;
- bearer proofs that can be transferred without rewriting a central named
  account after every exchange;
- keyset-bound units that keep unrelated obligations distinct;
- local and remote communication paths for presenting and reconciling claims;
- durable evidence of issuance, redemption, retirement, and policy changes;
  and
- software-verifiable controls against replay and double spending.

These capabilities change the cost, speed, privacy, and portability of
institutional coordination. They do not remove the need for judgment,
governance, trust, care, or recourse.

## Privacy and accountability can coexist

Conventional digital credit systems often make the operator's central account
database aware of every holder and transfer. Clear explores a different
balance. Blind-signed Mint Notes can move as private bearer instruments, while
the mint still validates proofs and prevents the same note from being redeemed
twice.

This does not provide perfect anonymity. Devices, networks, redemption sites,
and surrounding workflows can reveal metadata. Nor should privacy erase
institutional accountability. Issuance authority, total supply, treasury
grants, redemption, retirement, and settlement policy should remain
reviewable without publishing each person's complete transaction history.

That balance reflects Mainstay's broader governance statement: **Our House.
Our Rules. Our Business.** A community can operate legitimate, documented
rules for its own programs while treating the private affairs of members,
guests, staff, and participants with appropriate confidentiality.

## Clearing is governance

Clearing is sometimes presented as a purely mechanical back-office process. In
practice, it expresses policy.

Someone must decide which claims are eligible, which providers participate,
what counts as fulfillment, how exceptions are handled, when liabilities are
retired, and what happens when the instrument cannot be honored as expected.
Those decisions should be visible before value is issued, not invented after a
dispute.

Graeber's larger lesson is relevant here. Credit arrangements are never only
technical. They express social expectations and moral judgments about what is
owed, by whom, to whom, and under what conditions an obligation has been
satisfied or should be changed. Better digital evidence can make those choices
more legible, but it cannot make them neutral.

## Local capability within wider systems

A locally governed credit system does not require withdrawal from national
currency, banks, payment networks, or public institutions. Different systems
can serve different purposes.

A resort can accept ordinary payment while using bounded credits to coordinate
guest benefits. A co-working facility can use bank payments for membership and
service credits for shared resources. An Indigenous government or community
organization can define a program under its own procedures while maintaining
the regional and national relationships relevant to funding, reporting, law,
and service delivery.

Mainstay calls this **cooperative independence**. Local capability provides a
dependable place from which to participate in wider systems. It does not imply
self-sufficiency, universal acceptance, or freedom from outside obligations.

## Policy implications

A community or institution evaluating a digital value system should ask:

1. What real relationship or obligation does the proposed unit represent?
2. Who has legitimate authority to issue it, and how is that authority
   evidenced and limited?
3. Who is expected to accept it, and is acceptance genuinely voluntary?
4. Can holders understand redemption, expiry, conversion, and settlement
   before accepting the instrument?
5. Does transfer preserve appropriate privacy without hiding aggregate supply
   or treasury responsibility?
6. Can the issuer clear, reconcile, and retire claims with durable evidence?
7. What recourse exists when a claim is disputed or an obligation cannot be
   fulfilled?
8. Can the system remain available locally and reconnect to wider services
   without changing the identity of the unit or issuer?
9. Are unrelated currencies, credits, and issuer obligations kept visibly
   separate?
10. Can the technology be replaced without erasing the institution's records,
    authorities, outstanding claims, or obligations?

These are treasury and governance questions before they are software
questions.

## Mainstay's role

Mainstay coordinates the practical components without becoming the issuer or
the source of value:

- Clear provides governed Mint Notes and the mint-side clearing machinery;
- Acorn gives holders portable wallet authority and bearer-proof custody;
- the Clerk function preserves policies, appointments, authorizations, and
  evidence associated with treasury actions;
- Grove and Spurline provide local storage and signed-event availability; and
- Mainstay presents holdings, authority, transfer state, availability, and
  reconciliation through one local-first experience.

The responsible community or institution still defines the promise, appoints
its authorities, recognizes participants, operates the clearing process, and
decides what settlement means.

## Conclusion

Graeber's account asks us not to begin the history of value with strangers
swapping goods until they invent coins. It begins much closer to home: people
living in continuing relationships, remembering contributions, extending
trust, making promises, allocating resources, and deciding when obligations
have been fulfilled.

Credit, transfer, and clearing are therefore not obsolete practices waiting to
be replaced by a novel digital currency. They are enduring social capabilities.
Mainstay and Clear explore how communities can exercise them with modern
affordances: stronger privacy, verifiable authority, portable instruments,
clearer accounting, and local availability.

The aim is not to automate society. It is to give society better tools for work
it has always had to do together.
