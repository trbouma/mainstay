# White-Label Branding and Experience Profiles

## Status

This is a proposed design for layered Mainstay and installation-level branding.
It defines the ownership boundaries, profile schema, inheritance model, storage
model, application contract and implementation sequence for presenting Mainstay
as venue infrastructure behind a branded member experience. It does not
implement branding yet.

## Positioning

**Mainstay provides the invisible private venue infrastructure; the venue owns
the member experience.**

A branded deployment should look and speak like its venue throughout the wallet
and member-facing pages. Mainstay coordinates the local services behind that
experience without requiring Mainstay to be the public product name. Another
operator can run the same software with a different experience profile and no
fork of Safebox Web or the infrastructure services.

This supports the broader product proposition: private venue infrastructure
for funds and records that remains close to the venue while preserving the
member's control over their own identities, funds and data.

## Decision Summary

The proposed first model is:

1. Mainstay can manage reusable base experience profiles for a family, operator
   or group of related installations.
2. Each installation selects one base profile and may maintain one constrained
   instance override.
3. Mainstay resolves those layers into one versioned, validated effective
   profile with local, read-only assets.
4. Mainstay's dashboard and Safebox Web consume the same effective profile.
5. Member-facing Safebox Web uses the experience owner as its primary product
   identity.
6. Mainstay remains discoverable in operator and technical metadata even when
   member-facing attribution is intentionally absent.
7. Clear, Grove and Spurline retain their service names and protocol identities;
   they do not become venue-branded services at the protocol layer.
8. Branding never changes an `npub`, keyset ID, mint unit, blob digest, endpoint
   scope, commissioning relationship or member-controlled identity.
9. No configured profile means that each application uses its built-in native
   branding.
10. An explicitly configured but invalid effective profile is a startup error.
    The system must not silently present a mixture of venue and default
    branding.
11. The first release requires an application restart to activate a changed
   profile. Hot reload and relay-backed distribution remain future work.

## Layered Management Model

One installation still has exactly one active member experience. The layering
exists to manage that experience consistently, not to combine several brands
on one page.

```text
built-in product defaults
        ↓
Mainstay-managed base profile
        ↓
instance-managed override
        ↓
validated effective profile
        ↓
Mainstay dashboard + Safebox Web
```

The built-in profile keeps development and an unbranded installation simple. A
managed base profile can represent a community, hospitality group, co-working
network or another organization that wants a consistent identity across its
Mainstay installations. An instance override captures genuinely local details,
such as a property name, local logo, support desk, language or approved accent
color.

Precedence is explicit: an allowed instance value replaces the corresponding
base value; an absent instance value inherits the base. Applications never
perform this merge themselves. Mainstay resolves the layers, validates the
result and installs one immutable effective snapshot for every consuming
application.

### Override policy

Instance customization is field-based, not an unrestricted JSON merge. The
schema defines which semantic fields are potentially overridable, and a managed
base profile may narrow that list for installations using it. It may not add
new executable or security-sensitive fields.

Reasonable instance-managed fields include:

- public name, short name and local tagline;
- approved logo, mark, favicon and social image;
- local support, home, privacy and terms links;
- an approved subset of semantic colors;
- locale and allowlisted member terminology; and
- optional local contact or location text.

Mainstay-managed fields include:

- schema and compatibility version;
- the baseline semantic palette and accessible fallback values;
- the terminology allowlist and protected security language;
- permitted asset types, dimensions and size limits;
- attribution and technical-identity requirements; and
- the list of fields an instance may override.

This is a governance choice, not a technical claim that central management is
always superior. A fully independent installation can select an independently
managed base profile and retain broad local control. A group-operated deployment
can keep a shared identity while deliberately delegating local presentation
choices.

### Management operations

Mainstay should provide one administrative surface for both levels:

```text
mainstay-local brand list
mainstay-local brand validate <profile-directory>
mainstay-local brand assign <profile-id> --instance <instance>
mainstay-local brand override <override-directory> --instance <instance>
mainstay-local brand preview --instance <instance>
mainstay-local brand diff --instance <instance>
mainstay-local brand activate --instance <instance>
mainstay-local brand rollback --instance <instance>
```

The same operations can later be exposed through the authenticated Mainstay
dashboard. Command and dashboard actions must use the same validator, resolver
and atomic activation path.

## Roles and Boundaries

### Experience owner

The experience owner is the venue whose name, language and visual identity a
member encounters. In a branded installation, the selected venue is the
experience owner.

Subject to the selected profile's override policy, the experience owner
controls:

- public product name, short name and tagline;
- logos, icon, favicon and social preview image;
- approved presentation colors and typography choices;
- member-facing terminology;
- support, privacy and terms links; and
- optional Mainstay attribution on member-facing surfaces.

### Infrastructure operator

The Mainstay operator manages the available base profiles, selects which one an
installation uses, validates any instance override and activates the effective
snapshot. The operator may also be the experience owner, but the roles are not
assumed to be identical.

The operator controls deployment, service commissioning, endpoint policy,
backups and recovery. A brand profile does not grant operator authority.

### Member

Branding must not weaken or obscure the member's control. The member's Acorn,
`npub`, wallet state, bearer tokens, encrypted records and recovery material
remain independent of the venue's visual identity.

### Infrastructure services

Clear, Grove and Spurline keep their own service identities and technical
names. A venue may describe their capabilities in its own language, but it
must not rewrite signed descriptors or protocol identifiers to simulate a
different cryptographic identity.

## Experience Surfaces

The profile initially applies to two surfaces:

| Surface | Audience | Branding behavior |
| --- | --- | --- |
| Safebox Web | Members and recipients | Venue-first name, assets, colors, language and links |
| Mainstay dashboard | Local operators | Venue presentation with explicit Mainstay technical identity and service status |

Safebox Web should not require a visible "Mainstay" label in routine member
workflows. About, diagnostics and service-information surfaces may identify the
software and infrastructure without competing with the venue brand.

The dashboard has a different obligation. It may carry the venue's visual
profile, but it must continue to identify the Mainstay installation, its
installation `npub`, commissioning state, software version and actual component
names. Operators must always be able to tell what they are administering.

Clear, Grove and Spurline home pages remain technical service surfaces in the
first release. Extending venue presentation to those pages is unnecessary and
could blur service boundaries.

## Profile Schema

The canonical base file is `brand.json`. A proposed version-one profile is:

```json
{
  "schema": "org.mainstay.experience-profile",
  "schema_version": 1,
  "id": "example-venue",
  "management": {
    "instance_overrides": [
      "name",
      "short_name",
      "tagline",
      "assets.logo",
      "assets.mark",
      "links.home",
      "links.support",
      "localization.default_language",
      "localization.available_languages",
      "localization.copy"
    ]
  },
  "name": "Example Venue",
  "short_name": "Venue",
  "tagline": "Private venue infrastructure",
  "description": "A private place for member-controlled funds and records.",
  "assets": {
    "logo": "assets/logo.svg",
    "mark": "assets/mark.svg",
    "favicon": "assets/favicon.png",
    "social_preview": "assets/social-preview.jpg"
  },
  "colors": {
    "primary": "#123456",
    "accent": "#C47A3A",
    "background": "#F7F8F6",
    "surface": "#FFFFFF",
    "text": "#17211F",
    "muted_text": "#52605D",
    "success": "#287A52",
    "warning": "#A36216",
    "danger": "#A43D3D"
  },
  "terminology": {
    "user": "member",
    "wallet": "wallet"
  },
  "localization": {
    "default_language": "en",
    "available_languages": ["en", "fr"],
    "copy": {
      "fr": {
        "tagline": "Une infrastructure privée pour votre communauté",
        "description": "Un espace privé pour les fonds et les dossiers sous le contrôle des membres.",
        "terminology": {
          "user": "membre",
          "wallet": "portefeuille"
        }
      }
    }
  },
  "links": {
    "home": "https://example.com",
    "support": "https://example.com/support",
    "privacy": "https://example.com/privacy",
    "terms": "https://example.com/terms"
  },
  "attribution": {
    "member_surfaces": "hidden",
    "operator_surfaces": "technical"
  }
}
```

An instance override is a partial document named `brand.override.json`. It uses
the same semantic field names but may contain only fields permitted by the base
profile's override policy. Omission means inheritance; `null` does not mean
deletion unless the schema explicitly allows that field to be cleared.

The base profile's `management.instance_overrides` list can only narrow the
override paths supported by Mainstay's schema. It cannot make an otherwise
protected field overridable.

The active instance metadata records the base profile ID, base version and
digest, instance override digest, and effective profile digest. These values
make updates and support conversations precise without treating branding as
authority evidence. A minimal `selection.json` therefore identifies the base
profile and expected version; it does not duplicate presentation values.

The schema deliberately contains presentation and navigation values only. It
does not contain private keys, service routes, mint URLs, relay URLs, keyset
IDs, operator identities or permissions.

### Constrained terminology

Terminology overrides use an allowlist of semantic keys rather than arbitrary
template replacement. This prevents a profile from changing security language,
legal claims, currency units or protocol terms accidentally. Each application
owns the fallback and context-sensitive wording for every supported key.

### Localization ownership

Localization and white labelling are related but distinct. The experience
profile supplies venue-specific copy that an application cannot reasonably
translate itself: names, taglines, descriptions, approved terminology and
local links. Each application owns the translation catalogs for its interface,
including headings, controls, state descriptions, validation, security,
recovery and error messages.

Mainstay coordinates preferences; it does not maintain one family-wide catalog
of application strings. A locale is resolved in this order:

```text
explicit choice for the current application
    -> member's saved language preference, when supported by the application
    -> browser Accept-Language on a first or stateless visit
    -> instance default from the effective experience profile
    -> application's built-in default and fallback language
```

An application uses only the inputs available in its context. A stateful
member application may save an explicit choice in its protected preference
store. A stateless service homepage may retain the choice in a bookmarkable
query and negotiate an initial visit from `Accept-Language` without creating a
new user-tracking mechanism.

The profile uses canonical BCP 47 language tags. Its
`available_languages` list describes the venue-specific copy supplied by the
experience owner; it does not claim that every application has complete
interface coverage for every listed language. At runtime, an application
intersects the requested locale with its own supported languages and reports
the actual document language accurately.

Missing interface messages fall back through the application's own catalog
rules. Missing venue-specific copy falls back to the profile's default-language
value. A profile must not inject translations for protected recovery, custody,
transaction or security messages through terminology overrides.

Safebox Web's server-side gettext design is the family reference: translation
functions are bound per representation, shared template state is not mutated
per request, and user-authored values and protocol identifiers are not
translated. Other applications may use a different library when appropriate,
but should preserve those behavioral boundaries.

Clear, Grove and Spurline own the small vocabularies on their service home
pages. Localizing those pages is desirable but not a prerequisite for their
core service operation. Their JSON APIs, protocol values, machine-readable
error codes and technical identifiers remain stable and untranslated.

The family-wide implementation profiles, locale resolution rules, migration
threshold and translation review requirements are defined in the
[Product-Family Localization Design Note](LOCALIZATION-DESIGN-NOTE.md).

### Colors and typography

Applications consume semantic color tokens, not venue-supplied CSS. At load
time they validate color syntax and calculate required contrast for text,
controls, focus indicators and status states. An invalid or inaccessible
combination fails validation with a precise operator error.

The first release should use the application's bundled fonts or a system font
stack. Arbitrary remote font URLs would create availability, privacy and
content-security-policy dependencies that conflict with local-first operation.

### Assets

Asset paths are relative to the directory of the base or override document that
declares them. They cannot escape that source directory and cannot be remote
URLs. Mainstay validates and copies selected assets into the effective
snapshot; applications validate file type, size and dimensions again before
serving them.

Raster assets should use PNG, JPEG or WebP. SVG logos may be supported only
after sanitization or with a deliberately restricted static SVG policy; an
operator-supplied SVG must not become a script execution path. Applications
serve assets with explicit content types, safe cache headers and their existing
content security policy.

## Storage and Container Contract

Mainstay keeps reusable managed profiles outside any one instance. For an
instance named `mainstay-venue`, the catalog and installed layers are arranged
as follows:

```text
<mainstay-data-parent>/
├── brand-catalog/
│   └── example-venue/
│       ├── brand.json
│       └── assets/
└── mainstay-venue/
    ├── .env.recovery
    ├── branding/
    │   ├── selection.json
    │   ├── brand.override.json
    │   └── effective/
    │       ├── brand.json
    │       └── assets/
    ├── mainstay-control/
    ├── safebox-web/
    ├── spurline/
    ├── grove/
    └── clear/
```

The effective directory is generated, not edited. Mainstay mounts only that
directory read-only into the dashboard and Safebox Web:

```yaml
volumes:
  - ${MAINSTAY_EFFECTIVE_BRAND_ROOT}:/app/branding:ro
environment:
  MAINSTAY_BRAND_PROFILE: /app/branding/brand.json
```

The exact variable names remain an implementation detail until the first
integration. There should be one effective installed copy per instance, not
duplicated application-specific copies that can drift. A shared catalog may be
managed once for several local instances, but each instance retains its own
selection, override, resolved assets and rollback history.

`branding/` is included in instance backup, teardown and recovery boundaries.
The recovery copy of `.env` records whether branding is enabled and the
effective profile path, while the selection, override, resolved profile and
assets are backed up as files. The shared catalog has its own management backup
boundary. A recovered instance must validate its effective snapshot before
starting either branded application, even when the original catalog source is
temporarily unavailable.

## Installation and Update Lifecycle

The installer should eventually offer four choices:

1. use native Mainstay and Safebox branding;
2. select a profile already available in the Mainstay brand catalog;
3. install a profile from a local directory, optionally with an instance
   override; or
4. abort and prepare the profile before continuing.

Before making changes, installation preflight validates the schema, assets,
links, contrast and destination path. The final review shows the profile ID,
experience name, source and instance overrides. Installation resolves and
copies the complete effective snapshot atomically into the instance root and
records the base, override and effective digests.

Updating either layer is an explicit operator action. The update command
resolves the candidate base and instance override, validates the complete
effective result, stages it beside the current snapshot, atomically activates
it, and recreates the dashboard and Safebox Web containers. A failed validation
or restart leaves the previously installed snapshot active. Editing files
inside the active effective directory is prohibited because it bypasses
validation and audit history.

A managed base update must never unexpectedly erase an instance override. If a
new base version makes the override invalid or no longer permits one of its
fields, Mainstay rejects that candidate for the instance and reports the exact
conflict. Other compatible instances may still adopt the update.

A catalog update and an instance activation are separate actions. Mainstay may
validate a new base against every assigned instance and present a compatibility
report, but it does not silently activate the update everywhere. An operator
can approve compatible instances individually or as an explicit batch.

Fast creation of disposable instances remains possible: selecting the native
profile requires no additional input. A named profile is an optional packaging
step, not a new requirement for local testing.

## Runtime Contract

Each consuming application should expose one internal brand-provider interface
that returns validated semantic values. Templates and handlers must not read
JSON or environment variables independently.

The provider has three states:

```text
no configured profile
    -> return the application's built-in native profile

configured effective snapshot validates completely
    -> return that resolved profile without reading its source layers

configured effective snapshot is missing or invalid
    -> refuse startup with an operator-readable error
```

This prevents partial branding, such as a venue logo beside a Safebox title or
a stale social image. All browser assets and metadata derive from the same
validated profile, including page titles, application name, favicon, manifest,
Open Graph fields and QR-page presentation.

Protocol responses retain protocol-defined values. Technical `/health` and
`/info` responses continue to report the real component and version. They may
add a non-authoritative presentation block:

```json
{
  "service": "safebox-web",
  "version": "0.1.0",
  "experience": {
    "profile_id": "example-venue",
    "name": "Example Venue",
    "base_digest": "sha256:...",
    "override_digest": "sha256:...",
    "effective_digest": "sha256:..."
  }
}
```

The `experience` block is unsigned presentation metadata. It is not evidence
that the venue operates, commissions or controls the service.

## Identity and Trust

Brand identity, service identity and authority evidence answer different
questions:

```text
experience profile
    -> how should this installation present itself?

service npub
    -> which stable service is this?

operator attestation
    -> which authority has commissioned that service relationship?

member identity
    -> which keys and resources does the member control?
```

A venue logo is not commissioning evidence. An operator attestation does not
grant rights to a trademark. Applications must not infer either relationship
from the other.

Profile signing may be added later so an operator can verify that a package was
published by an expected experience owner. That would protect distribution
integrity; it would still not replace Mainstay service commissioning.

## Local-First and Future Resolution

The installed effective profile must work without DNS or internet access.
Assets are local and links are optional. An unavailable support link must not
prevent wallet operation.

The profile ID is a stable local label, not a global identity. A future signed
profile could be addressed by an experience-owner `npub` and synchronized over
Nostr, Grove or FIPS-aware infrastructure. Mainstay would resolve and verify a
new version, then install a local copy. Runtime rendering would still use the
validated local package rather than depending on a live remote service.

This keeps branding compatible with Mainstay's identity-based direction while
avoiding a premature dependency on DNS, HTTPS or a central theme registry.

## Security and Privacy Requirements

- Never permit templates, scripts or executable code in a profile.
- Never interpolate profile text as raw HTML.
- Restrict source asset paths to the declaring layer and effective asset paths
  to the generated snapshot root.
- Reject oversized, malformed or unsupported assets.
- Permit only expected `https://` links, with an explicit development exception
  if local links are needed.
- Preserve visible security, recovery and custody language even when terminology
  overrides are enabled.
- Do not send profile usage analytics or fetch remote assets by default.
- Do not expose filesystem paths in public responses.
- Keep technical component identity available to authenticated or local
  operators even when member-facing attribution is hidden.

## Implementation Sequence

### Phase 1: Profile package and validation

- Define a typed schema and JSON Schema fixture in Mainstay.
- Define the base-profile, instance-override and effective-profile contracts.
- Add `mainstay-local brand validate`, `preview` and `diff` commands.
- Add native and generic venue example profiles with test assets.
- Define field-level override policy and deterministic profile resolution.
- Define atomic installation, digesting, rollback and recovery behavior.

### Phase 2: Safebox Web integration

- Introduce one brand-provider abstraction with native fallback.
- Apply it to navigation, wallet pages, onboarding, page metadata, favicon,
  social preview and installable-app metadata.
- Resolve localized brand copy alongside Safebox Web's existing server-side
  gettext catalogs without combining their ownership.
- Add responsive and accessibility tests for both profiles.
- Preserve service and Acorn identity boundaries in `/info` and diagnostics.

### Phase 3: Mainstay dashboard integration

- Consume the same effective profile and asset mount.
- Present the venue prominently while retaining explicit installation identity
  and component names for operators.
- Report the active profile ID and base, override and effective digests in local
  status output.
- Expose the same preview, diff, activation and rollback operations as the CLI.

### Phase 4: Installer and lifecycle integration

- Add native, catalog-profile, local-profile and abort choices to first
  installation.
- Add per-instance selection and constrained override management.
- Include branding in backup, recovery and destructive-teardown review.
- Add atomic base and override update commands with per-instance conflict
  reporting and rollback.

### Phase 5: Supporting service home pages

- Let Clear, Grove and Spurline each own a small translation catalog for their
  browser homepage.
- Support conservative locale selection and honest fallback to the service's
  source language.
- Keep JSON APIs, protocol fields, machine-readable errors and technical
  identifiers untranslated.
- Treat this phase as a presentation improvement, not a core-service release
  gate.

### Phase 6: Portable assurance

- Define optional profile-owner signing and verification.
- Explore relay, Grove and FIPS distribution without making rendering depend on
  external availability.
- Consider multiple profiles only if a real multi-venue installation model is
  adopted.

## Acceptance Criteria for the First Release

The first branding release is complete when:

1. Mainstay can retain and validate a reusable managed base profile;
2. one Mainstay installation can select that base and apply an allowed local
   override;
3. resolution produces one deterministic effective profile and digest;
4. Safebox Web and the dashboard visibly use the same effective profile;
5. a branded deployment contains no accidental Safebox or Mainstay branding on
   routine member-facing surfaces;
6. operator surfaces still reveal the actual Mainstay installation and service
   identities;
7. native branding works without a profile directory;
8. invalid configured profiles prevent startup instead of partially applying;
9. an incompatible managed update leaves the previous instance snapshot active
   and identifies the conflicting override;
10. assets work offline and the effective package is mounted read-only;
11. installation recovery preserves the base selection, override and exact
    effective assets;
12. security, custody and recovery language cannot be suppressed by terminology
   overrides; and
13. automated tests cover inheritance, override policy, deterministic
    resolution, validation, fallback, rollback, accessibility, responsive
    rendering, locale resolution and technical metadata boundaries.

## Open Questions

- Should a generic example profile ship in Mainstay for development, while
  production profiles live in separate private brand-package repositories?
- Should managed base profiles support a small number of named policy presets,
  or should every permitted override path remain explicit in each profile?
- Which instance fields should native Mainstay permit by default, and which
  should require an independently managed base profile?
- Which member-facing name should replace "Safebox" in wallet navigation, if
  any?
- Is Mainstay attribution entirely hidden from members or included on an About
  screen?
- Which legal links and experience-owner details are mandatory for a profile?
- Should sanitized SVG be supported initially, or should version one require
  raster assets?
- Does a future Mainstay installation ever host more than one venue profile, or
  should that always require separate installation boundaries?

One effective profile per installation should remain the default until those
questions have concrete operational answers.
