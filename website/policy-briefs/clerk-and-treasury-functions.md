---
title: Clerk and Treasury Functions
description: Why sustainable communities need durable records and accountable ways to transfer value.
---

# Clerk and Treasury Functions

**Policy brief**

## Core proposition

Every institutionally sustainable community needs two enduring capabilities:

1. a way to preserve authoritative records and establish what follows from
   them; and
2. a way to account for, authorize, and transfer value.

Mainstay calls these the **Clerk function** and the **Treasury function**.
They are not new inventions, software product names, or mandatory job titles.
They are functional descriptions of work that communities and institutions
have carried out in many different forms for a very long time.

The technology is new. The institutional needs are not.

## The Clerk function: anchoring records

A community must be able to preserve consequential records: decisions,
appointments, permissions, agreements, obligations, entitlements, receipts,
registrations, policies, and evidence of completed acts. It must also be able
to answer who created or authorized a record, which exact version is being
considered, and what status or consequence follows under the community's own
rules.

This is the Clerk function. Historically, it has been carried through memory,
witnesses, seals, minutes, registries, ledgers, archives, and public offices.
The function need not belong to one person called a clerk, and it need not take
the same institutional form in every community.

In a digital environment, anchoring a record means more than placing a file in
cloud storage. A durable record should retain:

- the identity of the exact document, event, or artifact;
- evidence of who authorized or attested to it;
- the rules under which it is interpreted;
- its relationship to later amendments, transfers, revocations, or decisions;
- appropriate controls over disclosure and access; and
- enough portability to remain understandable beyond the application that
  created it.

Anchoring does not mean making every record public, permanent, or immutable.
Communities must decide what should be recorded, who may see it, how long it
should be retained, and which authority gives it effect. Technology can
preserve evidence and provenance; it does not replace those governance
decisions.

## The Treasury function: transferring value

A community must also be able to account for and move value. That can include
money, credits, benefits, allowances, vouchers, claims, obligations, service
units, or other instruments recognized under a defined policy.

This is the Treasury function. It includes more than making payments. A
sustainable treasury capability must be able to distinguish:

- who has authority to issue or authorize value;
- what unit or instrument is being used;
- what obligation or reserve stands behind it;
- who currently holds or controls it;
- whether it can be transferred;
- where and by whom it is accepted;
- how it may be redeemed, settled, reconciled, or retired; and
- what evidence supports the resulting accounts.

The Treasury function need not be centralized in one office, and value need
not be issued as a general-purpose currency. A community may use national
money for some purposes, locally governed service credits for others, and
institutional records to establish eligibility or authorization. The important
requirement is that authority, liability, transferability, acceptance, and
settlement remain explicit.

## Why the functions belong together

Records and value are deeply connected. A treasury action often depends on a
record: an approved budget, completed task, membership decision, entitlement,
invoice, or authorization. A consequential record may in turn create a claim,
release an obligation, or justify a transfer.

```text
Clerk function                         Treasury function

Who decided?                          Who authorized value?
What record exists?                   What instrument exists?
Which rules apply?                    What obligation supports it?
What follows from the evidence?       Can it be transferred or redeemed?
```

The functions should cooperate without being collapsed. A record system must
not silently become a mint. A payment application must not become the sole
authority for the agreement or entitlement behind a payment. Clear boundaries
allow each function to preserve the evidence the other may need while
remaining answerable to the appropriate authority.

## Reconstituting an old capability

Mainstay is not proposing that communities abandon established institutions
for an unprecedented digital model. It starts from the opposite observation:
durable records and accountable treasuries are age-old institutional
capabilities. Many modern systems have merely relocated them into remote,
provider-controlled applications that may be difficult to inspect, move, or
use when connectivity or a vendor is unavailable.

Mainstay explores how to reconstitute these familiar functions using new
technical building blocks:

- cryptographic signatures for portable evidence of authorization;
- stable public-key identities that do not depend on one domain name;
- content addressing for identifying exact encrypted records;
- local relays and storage for continued nearby availability;
- private ecash notes for transferring bearer value;
- explicit issuer, treasurer, keyset, and redemption relationships;
- dynamic resolution among internal, local, external, and future FIPS paths;
  and
- synchronization that can reconnect autonomous local operation to wider
  networks.

The result should feel less like an invention than a recovery of institutional
capacity. The record, authority, instrument, and obligation can once again be
held close to the people and organizations that rely on them, while remaining
portable enough to cooperate with outside systems.

## Local autonomy within wider networks

Local-first does not mean local-only. A community should be able to operate an
autonomous unit while using regional, national, commercial, or public services
when they are helpful and available.

A local Clerk function can preserve records and evidence during an upstream
outage, then synchronize or present them to an external institution when the
path returns. A local Treasury function can continue operating a bounded Clear
currency while national payments, external mints, or Lightning remain
available for other purposes.

Stable identities and replaceable paths are central to this cooperation. A
service, record, wallet, or currency unit should not become a different thing
merely because it moves between a local route and a wider network. This makes
autonomy compatible with federation instead of forcing a choice between
isolation and dependence.

## Authority remains with the community and its institutions

Mainstay provides supporting infrastructure. It does not appoint a community's
authorities, decide which records have legal or cultural significance,
guarantee an issuer's obligations, or compel anyone to accept a unit of value.

The community or responsible institution determines:

- who may exercise Clerk and Treasury responsibilities;
- which governance traditions and procedures apply;
- what evidence is recognized and what effects follow;
- what value instruments mean and who may issue them;
- who accepts or redeems those instruments;
- which information remains private; and
- when cooperation with an outside system is required.

This distinction is especially important across communities with different
legal orders, cultures, languages, and governance traditions. The terms Clerk
and Treasury describe capabilities, not a template that Mainstay imposes on
their organization.

## Policy implications

A community evaluating digital infrastructure should ask:

1. Can essential records and value remain available when the public Internet
   or a vendor is unavailable?
2. Are identities, records, and instruments portable beyond one application or
   domain name?
3. Are authority, service operation, custody, acceptance, and recognition
   clearly separated?
4. Can local operation reconnect to wider networks without rewriting identity
   or surrendering local governance?
5. Can consequential actions be verified from durable evidence rather than
   trusted only because an application database reports them?
6. Can the community choose its own retention, privacy, treasury, and
   recognition policies?
7. Can individual components be replaced without losing the records, keys, or
   value they helped manage?

These questions apply whether infrastructure is operated by a community,
municipality, Indigenous government, cooperative, campus, service provider, or
another institution.

## Mainstay's role

Mainstay coordinates local-first services supporting both functions:

- Acorn provides portable user authority, records, and wallet operations;
- Grove retains opaque, content-addressed encrypted blobs;
- Spurline preserves and carries signed events;
- Clear issues, transfers, validates, and retires governed Mint Notes;
- Stroma provides narrow Nostr signing and encryption primitives; and
- Mainstay supplies the installation context, service coordination, and
  continuity experience.

Each component remains independently useful. Mainstay coordinates their
boundaries without becoming the community's clerk, treasury, mint, archive, or
source of authority.

## Conclusion

A sustainable community needs institutional memory and an accountable way to
move value. Those are ancient requirements expressed here as Clerk and
Treasury functions.

Mainstay's contribution is not to invent the functions, but to help communities
reconstitute them with technology suited to present conditions: private,
portable, locally available, verifiable, and capable of working both
autonomously and across wider networks.

For the detailed architecture behind this policy frame, read the
[Clerk and Treasury Functions design note](https://github.com/trbouma/mainstay/blob/main/docs/CLERK-AND-TREASURY-FUNCTIONS.md).
