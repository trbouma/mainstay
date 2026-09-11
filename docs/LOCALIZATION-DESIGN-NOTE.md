# Product-Family Localization Design Note

## Status

Working standard for Mainstay and related applications.  
Decision date: 2026-09-11

## Purpose

This note defines how the Mainstay product family localizes human interfaces
without centralizing every product's language, weakening technical meaning or
requiring every application to use the same translation library.

The central decision is:

> Share one localization contract across the family, while choosing
> implementation machinery in proportion to each application's interface.

Safebox Web and Clear illustrate the distinction. Safebox Web is a stateful,
member-facing application with many views and a growing vocabulary. It uses
gettext catalogs and retains a member's preference in its encrypted session.
Clear has a small, public service homepage and no member session. It uses a
compact application-owned catalog, a bookmarkable language query and browser
language negotiation. The mechanisms differ because the applications differ;
their behavioral boundaries are the same.

## Goals

The family localization model should:

1. let people use an application in a language they understand;
2. let each application preserve the meaning of its own interface;
3. keep identities, values and protocol representations exact;
4. work locally without a translation service or upstream connection;
5. make language selection predictable, visible and reversible;
6. support community and professional review of translations;
7. keep white-label copy distinct from application interface text; and
8. scale from a small service homepage to a complete member application.

This note does not require every component to support every language. It does
not define locale-aware date, number or currency formatting, which may be added
as a separate concern without changing the ownership model below.

## Shared Family Contract

Every localized Mainstay-family application follows these rules regardless of
its framework or catalog format.

### Application ownership

Each application owns:

- its source messages and source language;
- its supported language list;
- its translation catalogs and fallback behavior;
- contextual and accessibility review;
- locale resolution for each representation; and
- tests proving that protected values are not translated.

Mainstay may coordinate an instance default or pass a member preference, but it
does not translate another application's messages or advertise support on that
application's behalf. A family-wide catalog would blur responsibility because
the application that presents a message is the component that knows its
context, risk and release state.

### Server-side representations

Server-rendered applications localize on the server. A translator is bound to
one request or representation and shared template state is never mutated for a
particular user. This prevents one concurrent request from changing another
request's language.

A browser may carry a selected language, but it should not carry a duplicate
translation engine when the interface is server rendered. Applications with a
substantial client-rendered interface may use an equivalent client catalog,
provided it preserves the same ownership, fallback and protocol boundaries.

### English source and honest fallback

English is currently the family source and fallback language. Source messages
remain readable and useful when no catalog is installed. Applications may
fallback per message, but they should advertise a language as supported only
when the intended interface surface has meaningful coverage.

Incomplete or provisional coverage must be stated honestly. Important
recovery, custody, security and transaction instructions must not be presented
as authoritative in a language that has not received appropriate contextual
review. English remains available as the reference representation.

### Stable technical meaning

Localization changes human presentation, not machine meaning. Applications do
not translate or rewrite:

- user-authored names, records or messages;
- configured organization, currency or service names;
- URLs, relay addresses, network routes or FIPS addresses;
- `npub`, `nsec`, keyset, unit, digest and event identifiers;
- bearer tokens, signatures or signed evidence;
- JSON field names and protocol enum values;
- machine-readable error codes; or
- amounts merely because the surrounding labels are translated.

An API remains stable when its service homepage changes language. Human API
descriptions may eventually be localized through a separate negotiated
representation, but the default machine contract must not vary silently.

### Local availability

All catalogs required for a supported interface ship with the application and
are included in its image, package or static assets. Rendering must not call an
external translation service. Language selection and fallback continue to work
when the Mainstay instance is operating only with local services.

## Locale Identification and Resolution

Applications use canonical BCP 47 language tags, including an explicit script
when it affects meaning, such as `zh-Hans`. They match conservatively:

1. use an exact supported tag when available;
2. apply an explicit, reviewed alias such as `zh-CN` to `zh-Hans`;
3. use a supported base language for compatible regional variants; and
4. otherwise use the application's source language.

An application must not cross a meaningful script or dialect boundary merely
to avoid English fallback. For example, Traditional Chinese must not be shown
with a Simplified Chinese document label unless the application has made that
choice explicit and reviewed it.

### Preference order

The effective language is resolved from the first applicable, supported input:

```text
explicit choice for the current application
    -> member's saved preference
    -> browser Accept-Language on a first or stateless visit
    -> instance default from the effective experience profile
    -> application's source language
```

An application uses only the inputs available in its context. Safebox Web can
save a member preference in its encrypted session. A stateless service page
such as Clear uses an explicit `?lang=` selection and then `Accept-Language`.
When Mainstay begins distributing an instance default, each application still
intersects it with its own supported language list.

An explicit choice should be easy to reverse. Stateful applications persist it
within their normal protected preference boundary. Stateless applications use
a shareable, bookmarkable URL rather than introducing a cookie solely for
localization.

### Representation metadata

A localized HTML response:

- sets the actual document language in `<html lang>`;
- sets `dir="rtl"` when the selected language requires it;
- emits `Content-Language` when the server controls response headers;
- emits `Vary: Accept-Language` when browser negotiation can affect output;
- presents language names in their own language in the selector; and
- preserves visible focus, keyboard operation and mobile text wrapping.

Pages selected through a query parameter remain distinct cache keys. The
`Vary` header protects the unqualified URL when it can be negotiated from a
request header.

## Two Implementation Profiles

The family standard defines two ordinary implementation profiles. These are
guidance, not new shared runtime dependencies.

### Full application profile

Use gettext or an equivalently mature catalog system for an application with
multiple screens, substantial message growth, plural forms, validation and
error text, or an external translation workflow.

Safebox Web is the reference implementation. Its gettext `.po` files are
editable review artifacts, compiled `.mo` files ship with the application, and
English source strings provide fallback. Its language preference belongs with
the connected member session because that session already carries protected
display preferences.

This profile provides:

- source-message extraction and catalog updates;
- translator-friendly files and tooling;
- plural and interpolation support;
- detection of stale or missing translations; and
- a sustainable workflow as interface copy changes.

The additional extraction, compilation and packaging steps are justified by
the size and lifecycle of the application.

### Compact service-page profile

An application-owned dictionary or similarly direct immutable catalog is
appropriate when all of the following are true:

- the localized surface is one compact operational page;
- the vocabulary is small and stable;
- messages do not need complex plural rules;
- the service has no existing member preference store; and
- maintainers can review the complete catalog in one place.

Clear is the reference implementation for this profile. Its service homepage
uses complete per-language dictionaries, an explicit language query and
`Accept-Language` fallback. Its JSON API remains unchanged.

The current Mainstay Local dashboard also uses this profile while it remains
one self-contained operational page. It uses semantic message keys and rejects
incomplete catalogs at startup. If the dashboard grows into a multi-page
control interface, it should move to the full application profile.

This is not a lesser localization policy. It is a smaller mechanism for a
smaller interface, with the same requirements for review, metadata, fallback,
concurrency and technical-value preservation.

### Migration threshold

A compact catalog should move to gettext or an equivalent system when any of
these becomes normal rather than exceptional:

- localization spans several pages or interface modules;
- messages change often enough that manual catalog comparison is unreliable;
- plural forms or structured interpolation are required;
- translators need standard exchange and review tools;
- untranslated or obsolete-message reporting becomes important;
- several developers routinely add interface copy; or
- the same application serves both a compact status page and a richer control
  interface.

Migration changes catalog tooling, not product behavior. Existing language
tags, URLs, fallback rules and protected-value boundaries should remain stable.

## Product-Family Responsibilities

| Component | Localization guidance |
| --- | --- |
| Mainstay | Coordinate instance defaults and effective profile copy; localize its own dashboard and operator interface |
| Safebox Web | Use the full application profile and retain supported member preferences in the encrypted session |
| Clear | Use the compact profile while the browser surface remains a single operational homepage |
| Grove and Spurline | Own compact homepage catalogs when localized; keep APIs and identifiers stable |
| Acorn and Stroma | Keep library and protocol behavior language-neutral; localize only human-facing tools they own |
| OpenETR | Own recordkeeping terminology and disclosure explanations; preserve digests, evidence and verification semantics |

Supporting-service localization is a presentation improvement, not a condition
for core service operation. A library does not gain a localization layer merely
because a consuming application has one.

## White Labelling and Local Copy

Localization and white labelling are related but independent layers.

The application catalog owns reusable interface language: controls, headings,
state explanations, validation, recovery, security and transaction messages.
An effective experience profile may provide venue-specific translated content:
the public name, tagline, description, approved terminology, support details
and local links.

Profile copy must be keyed by canonical language tag and may be used only when
the application supports that language for the relevant surface. Missing
venue-specific copy falls back to the profile's declared default. A profile
must not inject replacements for protected security, recovery, custody or
transaction language through unrestricted template substitution.

Applications render one resolved effective profile. They do not independently
merge Mainstay-managed and instance-managed branding layers while translating
a request.

## Translation Review

Translation is contextual product work, not only word substitution. Reviewers
should see the complete rendered workflow, including narrow viewports, status
changes, errors and accessibility labels.

Review is especially important for:

- custody, recovery, payment and security instructions;
- words that imply authority, verification, acceptance or legal effect;
- financial terms such as credit, liability, issue, redeem and balance;
- grammatical gender and plural forms around dynamic values;
- text embedded in copy confirmations and assistive labels; and
- language variants with community-specific dialect or orthography.

Indigenous-language support should be developed with fluent community members
who can review dialect, orthography and institutional context. A provisional
demonstration vocabulary must not be expanded into authoritative operational
instructions by automated or unreviewed translation.

Machine-assisted translation can produce a draft for low-risk, stable service
copy. A draft remains subject to human review and should be described as
provisional where misunderstanding could affect a person's funds, records,
identity or recovery options.

## Testing and Release Checklist

Every localized application should test, as applicable:

1. canonicalization and rejection of malformed language tags;
2. exact, regional, script and explicit-alias matching;
3. preference precedence and source-language fallback;
4. isolation of translators across concurrent requests;
5. correct HTML language, text direction and response headers;
6. presence and keyboard operation of the language selector;
7. catalog coverage for the advertised interface surface;
8. preservation of configured names, identifiers, URLs and user content;
9. stability of JSON APIs and machine-readable errors;
10. safe interpolation and HTML escaping in every language;
11. mobile wrapping for the longest translated labels and headings;
12. inclusion of compiled or source catalogs in production artifacts; and
13. operation without network access to a translation provider.

Release review should include at least one language with substantially longer
text than English and each materially different script or text direction that
the application advertises.

## Guidance for a New Application

Before adding localization to a new family application:

1. identify the human-facing surface and its authoritative owner;
2. inventory source messages separately from configured and protocol values;
3. choose the full or compact profile using the thresholds above;
4. declare supported BCP 47 tags and reviewed aliases;
5. define preference inputs available to that application;
6. bind translation state per representation;
7. implement honest fallback and response metadata;
8. package catalogs for offline operation;
9. document review status for each language; and
10. pass the family testing and release checklist.

The choice of gettext, a framework catalog or a compact dictionary is therefore
an engineering decision. Ownership, meaning, fallback, review and local
availability are product-family requirements.

## Related Notes

- [Mainstay House Style and Family Audit](MAINSTAY-HOUSE-STYLE.md)
- [White-Label Branding and Experience Profiles](WHITE-LABEL-BRANDING-DESIGN-NOTE.md)
- [Ecosystem Responsibility Boundaries and Iterative Development](ECOSYSTEM-RESPONSIBILITY-BOUNDARIES-AND-ITERATION.md)
