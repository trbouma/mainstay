# Mainstay Continuity Coordinator Design Note

Status: Exploratory design

## Purpose

Mainstay should be able to replicate selected local infrastructure data to
operator-configured external services. The immediate goal is continuity and
recovery, not making external infrastructure part of normal local operation.

The likely implementation is another service in the Mainstay deployment,
provisionally named `mainstay-continuity`. It would coordinate two different
replication mechanisms:

```text
internal Spurline events -> external Nostr relays
internal Grove blobs     -> external Grove services
```

These mechanisms can share policy, scheduling, health reporting, and durable
checkpoint state, but they should not be treated as one protocol. Nostr events
are synchronized as event sets. Grove resources are replicated as
content-addressed blobs.

## Ownership Decision

Continuity policy belongs to Mainstay, not to Grove or Spurline.

Mainstay knows which services belong to an installation, which external
destinations the operator has selected, what information may leave the local
environment, and whether the intended operation is backup, restoration, or
federation. Individual services should remain independently deployable and
should not acquire unexpected outbound behavior merely because they can run
inside Mainstay.

The boundary is:

```text
Mainstay
    -> owns destination policy, schedules, checkpoints, retries, and restore

Spurline
    -> owns Nostr event storage and relay protocol behavior

Grove
    -> owns content-addressed blob storage and Blossom behavior

Clear
    -> remains outside this replication mechanism
```

Clear requires transactionally consistent database backup and careful custody
of mint secrets. It must not be copied using event or blob synchronization.

## Proposed Docker Shape

The first implementation could add a dedicated container to the existing
Compose network:

```text
services:
    mainstay-continuity:
        depends_on:
            - mainstay-local
            - spurline
            - grove
        volumes:
            - continuity-data:/data
```

The service would have internal access to Mainstay's context manifest,
Spurline, and Grove. Outbound access would be limited by its configured
destinations. It would have its own persistent state rather than storing
checkpoints in the Mainstay dashboard volume or either service database.

The coordinator should have a stable service `npub`. Its `nsec` would be
generated during Mainstay bootstrap and managed like the other Mainstay
service identities. This identity would sign operational records and any
destination authorization that belongs to the coordinator. It must not sign
replacement events as users or imply control of the identities whose data is
being backed up.

## Operating Modes

The modes must be explicit because they have different trust and deletion
semantics.

### Export

One-way replication from the local installation to external destinations:

```text
local -> external
```

This is the recommended first release. Local services remain authoritative,
and external copies provide continuity if the installation is lost.

### Restore

An operator-initiated operation that reconstructs a local installation from
selected external destinations:

```text
external -> local
```

Restore should never begin automatically merely because local data appears
empty. It needs an explicit command, destination selection, identity checks,
and a report of what will be imported.

### Federation

Ongoing bidirectional exchange between installations:

```text
installation A <-> installation B
```

Federation is not equivalent to backup and should remain out of the first
implementation. It introduces authority, conflict, deletion, namespace, and
data-sharing questions that one-way export avoids.

## Spurline Event Synchronization

NIP-77 Negentropy is the preferred reconciliation mechanism when both relays
support it. Negentropy compares filtered event sets efficiently and identifies
event IDs missing from either side. It does not transfer the events itself;
the coordinator must use normal Nostr `EVENT` and `REQ` messages to move the
identified events.

The coordinator should reconcile one bounded policy filter at a time. A policy
might select:

- installation or service authors;
- wallet authors known to this Mainstay context;
- specific durable event kinds;
- a bounded creation-time window;
- explicitly included public application events.

The initial policy should exclude ephemeral events and avoid assuming that
every event accepted by the internal relay is appropriate for external
retention. Encrypted event content protects payload confidentiality, but
external relays can still observe authors, event kinds, timestamps, tags,
sizes, and activity patterns.

Because NIP-77 is optional, the coordinator needs one of two first-release
positions:

1. require Negentropy support and report incompatible targets; or
2. provide a checkpointed `REQ` and `EVENT` fallback.

The first option has a smaller and more testable implementation. The second
supports more relays but needs careful handling of pagination, duplicate
events, timestamp ties, and interrupted transfers.

Relay synchronization must preserve original signed events. The coordinator
must never recreate or re-sign them. Target relay acceptance and retention are
observable outcomes, not guarantees that Mainstay can impose.

## Grove Blob Replication

Grove resources are addressed by ciphertext SHA-256. Replication should
compare hashes rather than paths or original filenames:

```text
local Grove inventory
    -> external HEAD /<sha256>
    -> transfer missing ciphertext
    -> verify destination hash
```

Blossom BUD-04 mirroring may be used when the destination Grove can reach a
source URL. A Mainstay-internal Grove is normally unreachable from an external
service, so the coordinator will usually need to retrieve ciphertext over the
private network and upload it to the destination itself.

The coordinator needs an authoritative way to enumerate locally retained blob
hashes. Reading Grove's database or storage directory directly would couple
Mainstay to Grove internals. The preferred boundary is a narrow,
operator-authorized internal inventory interface that reports hashes and only
the metadata required for replication. The exact interface remains
undecided.

The coordinator must verify the local bytes against the inventory hash before
upload and require the destination's returned descriptor to contain the same
hash. A later `HEAD` confirms availability but not the bytes themselves;
periodic integrity audits would need to retrieve and hash the destination
content. The coordinator never needs plaintext, Acorn attachment keys, or
decrypted Safebox records because Grove stores ciphertext.

### Replica discovery

New Safebox records identify a blob with `blobsha256` and its original Grove
provider with `blob_service_npubs`. Mainstay cannot rewrite a user's encrypted
record merely because it created another replica.

Replica knowledge therefore needs a separate representation. Candidate
approaches include:

- a private, wallet-authored update adding another Grove service `npub`;
- a coordinator-maintained resource-location record keyed by blob hash;
- a Grove-issued availability record stating that it retains a given hash.

This question does not block backup. Mainstay can create and monitor external
copies before Acorn uses them automatically for ordinary resolution. Automated
failover should wait until replica discovery and authorization are defined.

## Destination Identity And Configuration

The long-term configuration should identify destinations by service `npub` and
resolve their current endpoints through the same service-resolution model used
elsewhere in Mainstay:

```text
destination service npub -> external HTTPS or WSS endpoint
```

The first implementation may accept explicit URLs as bootstrap hints, but it
should query the destination's service metadata and record the observed
`npub`. A later URL change should not silently select a different service
identity.

Illustrative settings, not yet a committed interface:

```env
MAINSTAY_CONTINUITY_ENABLED=false
MAINSTAY_CONTINUITY_MODE=export
MAINSTAY_CONTINUITY_INTERVAL_SECONDS=300
MAINSTAY_CONTINUITY_NOSTR_TARGETS=wss://relay.example
MAINSTAY_CONTINUITY_GROVE_TARGETS=https://grove.example
```

Configuration must distinguish Nostr relay targets from Grove targets even
when one operator provides both.

## Durable Coordinator State

The continuity volume should contain operational state only:

- target service identities and last observed endpoints;
- reconciliation checkpoints and bounded filter progress;
- last successful run per target and data class;
- retry schedules and failure summaries;
- hashes or event IDs with uncertain destination outcomes;
- restore manifests and operator acknowledgements.

It should not contain user private keys, decrypted records, Clear master
secrets, or a second authoritative copy of service databases. State writes
must be atomic so a container restart cannot advance a checkpoint beyond data
whose replication was confirmed.

## Failure And Deletion Semantics

The coordinator should be retryable and conservative:

- duplicate event publication and duplicate blob upload must be harmless;
- an uncertain write must be checked before it is repeated;
- one failing destination must not block healthy destinations;
- health must distinguish delayed, degraded, unauthorized, and incompatible;
- checkpoints advance only after destination confirmation;
- local service operation continues when every external target is offline.

Deletion must not be mirrored in the first release. Removing a local event or
blob does not necessarily mean an external continuity copy should disappear.
Conversely, retaining external copies indefinitely may violate operator or
user expectations. Retention and deletion require an explicit policy before
the coordinator propagates destructive actions.

## Mainstay Dashboard And CLI

The dashboard should eventually report, without exposing sensitive event or
resource details:

- coordinator identity and health;
- configured destination identities;
- last successful event and blob reconciliation;
- pending and failed item counts;
- oldest outstanding work;
- whether each target supports the preferred protocol;
- whether restore material is available.

Likely CLI operations include:

```text
mainstay-local continuity status
mainstay-local continuity sync
mainstay-local continuity verify
mainstay-local continuity restore --from <service-npub>
```

The exact commands should follow implementation experiments rather than being
treated as fixed by this note.

## Initial Delivery Plan

### Phase 1: observation

- Add a disabled `mainstay-continuity` service and private state volume.
- Resolve and verify configured destination service identities.
- Inventory eligible Spurline events and Grove hashes without transferring.
- Report compatibility, counts, and estimated transfer size.

### Phase 2: one-way export

- Reconcile bounded Spurline filters to one external relay.
- Copy missing Grove ciphertext to one external Grove service.
- Persist checkpoints and expose health and failure summaries.
- Keep local operation independent of destination availability.

### Phase 3: recovery

- Produce a signed or checksummed restore manifest.
- Add explicit dry-run and operator-confirmed restore commands.
- Verify restored event signatures and blob hashes.

### Deferred work

- bidirectional federation;
- automatic Acorn replica discovery and failover;
- propagated deletion;
- Clear database backup;
- FIPS-native transport adapters;
- signed destination or resolution evidence beyond observed service identity.

## Open Questions

1. Which Nostr authors and event kinds belong to an installation's default
   continuity set?
2. Should the first release require NIP-77 or implement a conventional relay
   fallback immediately?
3. What minimal internal Grove inventory interface avoids exposing storage
   implementation details?
4. Under which `npub` should an external Grove retain coordinator-uploaded
   ciphertext?
5. How should Acorns learn about replicas created after their records were
   written?
6. What retention and deletion policy should apply to external copies?
7. Should external destinations be shared installation-wide or selectable by
   individual Safebox users?
8. What evidence is sufficient before a restore target is trusted?

## References

- [NIP-77: Negentropy Syncing](https://github.com/nostr-protocol/nips/blob/master/77.md)
- [Blossom protocol and BUD index](https://github.com/hzrd149/blossom)
- [BUD-04 mirroring implementation notes](https://github.com/hzrd149/blossom-server#mirror-endpoint)
