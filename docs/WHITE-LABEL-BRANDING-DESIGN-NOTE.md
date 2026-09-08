# White-Label Branding and Experience Profiles

## Status

This is a proposed design for installation-level branding. It defines the
ownership boundaries, profile schema, storage model, application contract and
implementation sequence for presenting Mainstay as venue infrastructure behind
a branded member experience. It does not implement branding yet.

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

The proposed first profile is:

1. Mainstay owns one active experience profile per installation.
2. The profile is a versioned JSON document with local, read-only assets.
3. Mainstay's dashboard and Safebox Web consume the same installed profile.
4. Member-facing Safebox Web uses the venue as its primary product identity.
5. Mainstay remains discoverable in operator and technical metadata even when
   member-facing attribution is intentionally absent.
6. Clear, Grove and Spurline retain their service names and protocol identities;
   they do not become venue-branded services at the protocol layer.
7. Branding never changes an `npub`, keyset ID, mint unit, blob digest, endpoint
   scope, commissioning relationship or member-controlled identity.
8. No configured profile means that each application uses its built-in native
   branding.
9. An explicitly configured but invalid profile is a startup error. The system
   must not silently present a mixture of venue and default branding.
10. The first release requires an application restart to activate a changed
    profile. Hot reload and relay-backed distribution remain future work.

## Roles and Boundaries

### Experience owner

The experience owner is the venue whose name, language and visual identity a
member encounters. In a branded installation, the selected venue is the
experience owner.

The experience owner controls:

- public product name, short name and tagline;
- logos, icon, favicon and social preview image;
- approved presentation colors and typography choices;
- member-facing terminology;
- support, privacy and terms links; and
- optional Mainstay attribution on member-facing surfaces.

### Infrastructure operator

The Mainstay operator installs the profile, validates its files and decides
which installation uses it. The operator may also be the experience owner, but
the roles are not assumed to be identical.

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

The canonical file is `brand.json`. A proposed version-one profile is:

```json
{
  "schema": "org.mainstay.experience-profile",
  "schema_version": 1,
  "id": "example-venue",
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

The schema deliberately contains presentation and navigation values only. It
does not contain private keys, service routes, mint URLs, relay URLs, keyset
IDs, operator identities or permissions.

### Constrained terminology

Terminology overrides use an allowlist of semantic keys rather than arbitrary
template replacement. This prevents a profile from changing security language,
legal claims, currency units or protocol terms accidentally. Each application
owns the fallback and context-sensitive wording for every supported key.

### Colors and typography

Applications consume semantic color tokens, not venue-supplied CSS. At load
time they validate color syntax and calculate required contrast for text,
controls, focus indicators and status states. An invalid or inaccessible
combination fails validation with a precise operator error.

The first release should use the application's bundled fonts or a system font
stack. Arbitrary remote font URLs would create availability, privacy and
content-security-policy dependencies that conflict with local-first operation.

### Assets

Asset paths are relative to the profile directory. They cannot escape that
directory and cannot be remote URLs. Applications validate file type, size and
dimensions before serving them.

Raster assets should use PNG, JPEG or WebP. SVG logos may be supported only
after sanitization or with a deliberately restricted static SVG policy; an
operator-supplied SVG must not become a script execution path. Applications
serve assets with explicit content types, safe cache headers and their existing
content security policy.

## Storage and Container Contract

For an instance named `mainstay-venue`, the installed copy lives beneath the
instance data root:

```text
<instance-data-root>/
├── .env.recovery
├── branding/
│   ├── brand.json
│   └── assets/
│       ├── logo.svg
│       ├── mark.svg
│       ├── favicon.png
│       └── social-preview.jpg
├── mainstay-control/
├── safebox-web/
├── spurline/
├── grove/
└── clear/
```

The profile is durable installation configuration, not mutable application
data. Mainstay mounts the same directory read-only into the dashboard and
Safebox Web:

```yaml
volumes:
  - ${MAINSTAY_BRAND_ROOT}:/app/branding:ro
environment:
  MAINSTAY_BRAND_PROFILE: /app/branding/brand.json
```

The exact variable names remain an implementation detail until the first
integration. There should be one canonical installed copy, not duplicated
copies that can drift between containers.

`branding/` is included in instance backup, teardown and recovery boundaries.
The recovery copy of `.env` records whether a profile is enabled and its path,
but the profile and assets are backed up as files. A recovered instance must
validate the profile before starting either branded application.

## Installation and Update Lifecycle

The installer should eventually offer three choices:

1. use native Mainstay and Safebox branding;
2. install a profile from a local directory; or
3. abort and prepare the profile before continuing.

Before making changes, installation preflight validates the schema, assets,
links, contrast and destination path. The final review shows the profile ID,
experience name and source. Installation copies the complete profile atomically
into the instance root and records a digest of the installed contents.

Updating a profile is an explicit operator action. The update command validates
the candidate, stages it beside the current profile, atomically activates it,
and recreates the dashboard and Safebox Web containers. A failed restart rolls
back to the previously installed profile. Editing files inside the active
directory is discouraged because it bypasses validation and audit history.

Fast creation of disposable instances remains possible: selecting the native
profile requires no additional input. A named profile is an optional packaging
step, not a new requirement for local testing.

## Runtime Contract

Each consuming application should expose one internal brand-provider interface
that returns validated semantic values. Templates and handlers must not read
JSON or environment variables independently.

The provider has two states:

```text
no configured profile
    -> return the application's built-in native profile

configured profile validates completely
    -> return the installed venue profile

configured profile is missing or invalid
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
    "name": "Example Venue"
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

The installed profile must work without DNS or internet access. Assets are
local and links are optional. An unavailable support link must not prevent
wallet operation.

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
- Restrict asset paths to the installed profile root.
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
- Add a `mainstay-local brand validate <directory>` command.
- Add native and generic venue example profiles with test assets.
- Define atomic installation, digesting and recovery behavior.

### Phase 2: Safebox Web integration

- Introduce one brand-provider abstraction with native fallback.
- Apply it to navigation, wallet pages, onboarding, page metadata, favicon,
  social preview and installable-app metadata.
- Add responsive and accessibility tests for both profiles.
- Preserve service and Acorn identity boundaries in `/info` and diagnostics.

### Phase 3: Mainstay dashboard integration

- Consume the same installed profile and asset mount.
- Present the venue prominently while retaining explicit installation identity
  and component names for operators.
- Report the active profile ID and digest in local status output.

### Phase 4: Installer and lifecycle integration

- Add native, local-profile and abort choices to first installation.
- Include branding in backup, recovery and destructive-teardown review.
- Add an atomic profile update command with rollback.

### Phase 5: Portable assurance

- Define optional profile-owner signing and verification.
- Explore relay, Grove and FIPS distribution without making rendering depend on
  external availability.
- Consider multiple profiles only if a real multi-venue installation model is
  adopted.

## Acceptance Criteria for the First Release

The first branding release is complete when:

1. one Mainstay installation can select one validated local profile;
2. Safebox Web and the dashboard visibly use the same profile;
3. a branded deployment contains no accidental Safebox or Mainstay branding on
   routine member-facing surfaces;
4. operator surfaces still reveal the actual Mainstay installation and service
   identities;
5. native branding works without a profile directory;
6. invalid configured profiles prevent startup instead of partially applying;
7. assets work offline and are mounted read-only;
8. installation recovery preserves the selected profile and exact assets;
9. security, custody and recovery language cannot be suppressed by terminology
   overrides; and
10. automated tests cover validation, fallback, accessibility, responsive
    rendering and technical metadata boundaries.

## Open Questions

- Should a generic example profile ship in Mainstay for development, while
  production profiles live in separate private brand-package repositories?
- Which member-facing name should replace "Safebox" in wallet navigation, if
  any?
- Is Mainstay attribution entirely hidden from members or included on an About
  screen?
- Which legal links and experience-owner details are mandatory for a profile?
- Should sanitized SVG be supported initially, or should version one require
  raster assets?
- Does a future Mainstay installation ever host more than one venue profile, or
  should that always require separate installation boundaries?

The single-profile installation model should remain the default until those
questions have concrete operational answers.
