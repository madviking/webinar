Status: draft
Last reviewed: 2026-01-31

# Integration Layer — requirements

## 1) Goal

Provide a **tenant-configurable integration layer** that can reliably and safely exchange Queast domain events/data with external systems (starting with HubSpot and Pipedrive), with clear data contracts and operational guarantees.

## 2) Product requirements (functional)

### 2.1 Tenant installation & configuration

- Each tenant can enable one or more “integration connections” (e.g., HubSpot, Pipedrive).
- Configuration surface (v1 decision):
  - Tenant-facing configuration exists (tenant-wide) and is **tenant_admin-only**.
  - Admin-facing configuration exists for bootstrap/override/support.
- Connection cardinality (v1 decision):
  - Exactly **one connection per connector type** per tenant (for this stage).
- Rollout gating (v1 decision):
  - Integration UI/enablement is behind a feature flag / allowlist.
- Each connection has explicit configuration, including:
  - destination type (HubSpot vs Pipedrive vs generic webhook),
  - auth (OAuth/token as applicable),
  - mapping policy/version,
  - delivery mode (webhook push, partner API push, or both),
  - enable/disable toggles by event type.

### 2.2 Data delivery

- The integration layer can deliver data about:
  - Companies
  - People
  - Smart Signals (Actionable Signals; strict-only)
  - Job ads (as evidence references/links; not treated as a Signal)
- Delivery supports:
  - near-real-time push (event-driven),
  - replay/backfill (explicit, operator/tenant-triggered),
  - idempotency (dedupe keys per destination + event type).

### 2.3 Inbound (“two-way”) support — prepared in v1, light scope

- The integration layer must be designed for two-way integration.
- Initial inbound scope is intentionally light:
  - inbound events primarily “highlight” / “mark interest” in companies for a tenant by creating a **bookmark**.
- Inbound data must not be allowed to create Actionable Signals directly.
  - It may create tenant-side state like a “watchlist/bookmark/interest” marker (exact model TBD).
  - v1 decision: inbound “interest highlight” becomes a **bookmark**.
  - If identity resolution is ambiguous (or below threshold), the inbound event must be quarantined for manual review (match queue).

### 2.3 Contracts & versioning

- Every outbound payload is versioned:
  - `event_type`
  - `schema_version`
  - `occurred_at`
  - stable `idempotency_key`
- Backwards-compatibility policy is explicit (e.g., additive changes only within a major version).

### 2.4 Mapping & identity

- Support stable identity mapping between Queast entities and partner objects:
  - mapping store is per-tenant and per-connection,
  - supports upserts and lookups for company/person identifiers.
- Matching must support multiple strategies, configured per connection:
  - explicit partner object IDs (best),
  - domains / emails where available,
  - LinkedIn URLs (company and person),
  - fuzzy matching on names (company name matching), with confidence + reviewable outcomes.
- Fuzzy matching policy:
  - auto-link above a configurable confidence threshold,
  - record match provenance and confidence,
  - provide a place to manually review all matches (including auto-linked ones) and fix/unlink if needed.
- Clear ownership rules:
  - Queast is source-of-truth for Signals artifacts,
  - partner system may be source-of-truth for CRM fields (unless explicitly configured).

### 2.5 Webhook inbound handling (optional / phased)

- If inbound webhooks are supported (HubSpot/Pipedrive → Queast), they must:
  - authenticate and validate signatures,
  - be idempotent,
  - translate into internal events without writing SQL in routers (service/repository split).
  - record “match result” metadata (which strategy matched, confidence, and any ambiguities).

## 3) System requirements (non-functional)

### 3.1 Tenant safety & isolation

- Hard isolation by tenant_id for all configs, secrets, mappings, deliveries, and retries.
- Ensure no cross-tenant leakage in logs, metrics, or payload storage.

### 3.2 Reliability

- Delivery is retried with backoff on transient failures.
- Clear semantics per destination:
  - at-least-once delivery (default),
  - “exactly once” is not assumed; idempotency is required.
- Dead-letter / failure quarantine for repeated failures with operator visibility.

### 3.3 Performance & rate limiting

- Respect partner API rate limits and concurrency limits per tenant connection.
- Control blast radius by per-tenant and global throttles.

### 3.4 Observability & auditability

- Persistent delivery records with:
  - event metadata, destination, attempt count, last error, and final status.
- Correlation IDs and traceability from internal event → outbound delivery.
- Exported artifacts must be replayable without mutating history.
- A backfill/replay mechanism is required (at minimum for outbound).
- Logs are required for troubleshooting (with tenant-safety and PII constraints).

### 3.5 Security

- Secrets are stored encrypted and rotated (where supported).
- Webhooks are signed and verified (where applicable); support IP allowlists as defense-in-depth.

## 4) Signals-specific constraints (do not drift)

When exporting Smart Signals:
- Treat Smart Signals as **Actionable Signals** and obey the locked causal model.
- Technology tags are **decorations only** and must not be represented as causal “reasons” or eligibility gates.
- If exporting non-strict types (informational/legacy), payloads must include explicit contract metadata (e.g., `contract_mode`, `contract_version`) so destinations can treat them appropriately.
  - v1 decision: exporting informational/legacy types is **on by default** (still tenant-configurable).
- Prefer linking to canonical Signals docs over duplicating terminology:
  - `backend/app/signals/audit/README.md`
  - `backend/app/signals/audit/SKILL_signals_intent_system.md`
