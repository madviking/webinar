Status: draft
Last reviewed: 2026-02-01

# Integration Layer — data contracts (v1 draft, implementable)

This document defines the **canonical event contracts** used by Queast’s integration layer.

- Outbound: Queast delivers a canonical envelope to a destination (generic webhooks first; HubSpot/Pipedrive later).
- Inbound: external systems send a canonical-ish request that Queast validates and normalizes into internal actions (v1 scope: “company interest highlight”).

Vendor-specific connectors translate between these canonical shapes and partner APIs/webhook formats.

## 1) Versioning + backwards compatibility (policy)

### 1.1 `schema_version` is major-only

- `schema_version` is a major version string: `v1`, `v2`, ...
- Within a major (e.g., `v1`), changes are **additive-only**:
  - adding new optional fields is allowed
  - tightening validation (optional → required) is not allowed
  - renaming/removing fields is not allowed

### 1.2 Adding event types

Within `v1`, we may add new `event_type` values. Consumers MUST:
- ignore/record unknown `event_type` values safely, and
- not assume the list of event types is fixed.

If we ever need to change meanings or required fields in a breaking way, bump `schema_version` to `v2`.

### 1.3 Event naming + per-event versioning (v1)

- `event_type` is the **event name** (sometimes called “event_name” in other systems).
- We do **not** introduce a separate `event_version` field in `v1`.
  - Use `schema_version` for major version breaks.
  - Use additive-only payload evolution within `v1`.
  - Use `data.subject.version` (and domain-specific contract fields like `signal.contract_version`) to represent “this is a different logical update” for idempotency/deduplication.

## 2) Canonical envelope (outbound)

All outbound deliveries MUST be wrapped in this envelope.

### 2.1 Required fields

- `schema_version`: string, required. Must equal `v1`.
- `event_type`: string, required. One of the `v1` event types in §4.
- `event_id`: string, required. UUID (recommended: UUIDv7). Uniquely identifies a logical event instance.
- `occurred_at`: string, required. RFC3339 timestamp (UTC) for when the underlying domain change occurred.
- `produced_at`: string, required. RFC3339 timestamp (UTC) for when Queast produced/enqueued the event.
- `tenant_id`: integer, required. Queast tenant id (internal identifier).
- `idempotency_key`: string, required. Stable per **destination + logical event** (see §3).
- `data`: object, required. Event payload (schema depends on `event_type`).

### 2.2 Optional metadata (non-breaking, v1)

- `trace`: object (optional)
  - `correlation_id`: string (optional; recommended UUID)
  - `source`: string (optional; default `queast`)
- `integration`: object (optional)
  - `connection_id`: integer (optional; internal connection id)
  - `connector_type`: string (optional; e.g., `webhook|hubspot|pipedrive`)
- `actor`: object (optional; internal ids only; no PII)
  - `user_id`: integer (optional; Queast user id, if user-initiated)
  - `api_key_id`: integer (optional; if API key initiated)
  - `impersonated_by_user_id`: integer (optional; admin impersonation, if applicable)
- `privacy`: object (optional; safe-to-log metadata only)
  - `contains_pii`: boolean (optional; whether the payload includes PII fields)
  - `pii_fields_exported`: string[] (optional; e.g., `["work_email"]`)
  - `pii_policy`: string (optional; policy identifier/version)

Notes:
- `integration.connection_id` and `integration.connector_type` are **delivery-scoped** and may be injected by the dispatcher when creating per-connection delivery jobs.

### 2.3 Example

```json
{
  "schema_version": "v1",
  "event_type": "company.upserted",
  "event_id": "018d7e2f-7c52-7f4d-8c0c-0d3a8a3f5e6d",
  "occurred_at": "2026-02-01T07:00:00Z",
  "produced_at": "2026-02-01T07:00:01Z",
  "tenant_id": 12,
  "idempotency_key": "v1:webhook:42:company.upserted:company:12345:2026-02-01T07:00:00Z",
  "data": { "subject": { "type": "company", "id": "12345", "version": "2026-02-01T07:00:00Z" } }
}
```

## 3) Idempotency keys (required; implementable rules)

Idempotency keys prevent duplicate side effects at destinations when Queast retries deliveries or replays/backfills events.

### 3.1 Invariants

For a given destination:
- retries MUST reuse the same `idempotency_key` (and `event_id`)
- replays/backfills SHOULD reuse the same `idempotency_key` for the same logical event (to avoid duplicates)
- a genuinely different logical event MUST have a different `idempotency_key`

### 3.2 Required `data.subject` block

Every `v1` event payload MUST include:

```json
{
  "subject": {
    "type": "company|person|signal|job_ad_snapshot",
    "id": "string",
    "version": "string"
  }
}
```

Rules:
- `subject.id` MUST be stable and unique for that subject type within the tenant.
- `subject.version` MUST change when a new logical event should be emitted for the same subject.
  - For append-only events (e.g., `signal.published`), `subject.version` should be the publish timestamp or the signal id.
  - For upserts, `subject.version` should be the source record’s updated timestamp (preferred) or a snapshot identifier.

### 3.3 Canonical composition (recommended)

`idempotency_key` SHOULD be derived from these parts:
- `schema_version`
- `connector_type` + `connection_id` (destination identity)
- `event_type`
- `subject.type`, `subject.id`, `subject.version`

Recommended string format (human-readable; hashing is optional):

`{schema_version}:{connector_type}:{connection_id}:{event_type}:{subject.type}:{subject.id}:{subject.version}`

If a destination has strict length limits, use `sha256()` of the above string and base64url encode it, but still log the unhashed “debug string”.

### 3.4 Transport recommendation (HTTP)

For webhook-based deliveries, ALSO send `idempotency_key` as an HTTP header:
- `Idempotency-Key: <idempotency_key>`

## 4) `v1` event types + minimal payloads

### 4.1 `company.upserted`

Use when Queast wants a destination to create/update a company representation.

Required payload:

```json
{
  "subject": { "type": "company", "id": "<company_id>", "version": "<company_version>" },
  "company": {
    "company_id": 12345,
    "name": "Acme Inc"
  }
}
```

Optional fields (additive; v1-safe):
- `company.domain` (string)
- `company.website_url` (string)
- `company.linkedin_url` (string)
- `company.employee_count` (integer)
- `company.location` (string)

Notes:
- `company_id` references `data_companies.id` (read-only external table) but is stable as an identifier.
- `company_version` should be the best available “company record version” timestamp/identifier used for idempotency (see §3.2).

### 4.2 `person.upserted`

Use when Queast wants a destination to create/update a person/contact representation.

Required payload:

```json
{
  "subject": { "type": "person", "id": "<person_id>", "version": "<person_version>" },
  "person": {
    "person_id": 9876,
    "full_name": "Jane Doe"
  }
}
```

Optional fields (additive; v1-safe):
- `person.company_id` (integer; `data_companies.id`), if known
- `person.title` (string)
- `person.linkedin_url` (string)
- `person.email` (string; PII; may be omitted by policy/config)
- `person.phone` (string; PII; may be omitted by policy/config)

### 4.3 `signal.published` (strict Actionable Signal only)

Use when Queast publishes a Smart Signal that is a strict Actionable Signal.

Hard constraint:
- exports MUST NOT change Signals terminology/contracts
- treat Smart Signals as Actionable Signals and include contract metadata (`contract_mode`, `contract_version`) as produced by Queast Signals APIs

Canonical constraints:
- `backend/app/signals/audit/README.md`
- `backend/app/signals/audit/SKILL_signals_intent_system.md`

Required payload (minimum, implementable):

```json
{
  "subject": { "type": "signal", "id": "<signal_id>", "version": "<signal_published_at>" },
  "signal": {
    "id": 991,
    "tenant_id": 12,
    "company_id": 12345,
    "signal_type": "intent_opportunity",
    "contract_mode": "strict",
    "contract_version": "v1",
    "title": "Hiring spike suggests expansion",
    "summary_markdown": "…",
    "created_at": "2026-02-01T06:59:00Z",
    "updated_at": "2026-02-01T06:59:00Z"
  }
}
```

Strongly recommended (optional in v1):
- `signal.evidence` as an array of references shaped like `backend/app/signals/schemas.py::SmartSignalEvidenceItem`
- `signal.technology_tags` as decoration-only (same semantics as Signals tenant APIs)

### 4.4 `job_ad.snapshot_linked` (link-only; not a Signal)

Use when Queast wants to link a job-ad snapshot as evidence/context in a destination system.

Required payload:

```json
{
  "subject": { "type": "job_ad_snapshot", "id": "<job_ad_id>", "version": "<snapshot_version>" },
  "job_ad": {
    "job_ad_id": 555,
    "company_id": 12345,
    "title": "Senior Data Engineer",
    "url": "https://…"
  }
}
```

Optional fields (additive; v1-safe):
- `job_ad.published_at` (RFC3339 string)
- `job_ad.location` (string)
- `job_ad.remote_type` (string)

Notes:
- This event is informational evidence only and MUST NOT be treated as an Actionable Signal.

### 4.5 Inbound: `company.interest_marked` (external → Queast)

Inbound events are intentionally light and MUST NOT be treated as evidence that can create Actionable Signals.

v1 decision:
- inbound “interest marked” becomes a **tenant-wide company bookmark** in Queast (see Headless PM RFC doc #14)
- semantics are **idempotent ensure-bookmarked** (NOT toggle)

Required inbound request body:

```json
{
  "schema_version": "v1",
  "event_type": "company.interest_marked",
  "occurred_at": "2026-02-01T07:10:00Z",
  "idempotency_key": "v1:hubspot:9:company.interest_marked:partner_company_id:123",
  "data": {
    "partner": {
      "connector_type": "hubspot|pipedrive|webhook",
      "company_id": "string"
    },
    "company": {
      "domain": "example.com",
      "linkedin_url": "https://www.linkedin.com/company/example/",
      "name": "Example Inc"
    }
  }
}
```

Rules:
- `data.partner.company_id` is preferred and should be used for deterministic matching when present.
- If partner company id is missing, matching may fall back to domain/linkedin/name with safety rails and review queueing (Phase 2).

## 5) Explicit open questions (must be resolved later; not implied)

1) Person export policy: which PII fields (email/phone) are allowed by default vs behind explicit tenant config/consent?
2) What is the canonical representation of exported Signals inside HubSpot/Pipedrive (notes vs tasks vs custom objects) beyond Phase 0 webhooks?
3) What is the definitive `company_version` / `person_version` source in v1 (updated_at vs snapshot id) to make replays strictly de-dupe-safe?
4) Do inbound partners always provide a stable partner event id we can include in `idempotency_key`, or must we derive it solely from partner object id + occurred_at?
