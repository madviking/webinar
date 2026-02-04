Status: draft
Last reviewed: 2026-01-31

# Integration Layer — architecture overview (draft)

## 1) Architectural goals

- Provide a consistent **integration contract surface** independent of vendor specifics.
- Keep partner-specific logic isolated in “connectors/adapters”.
- Ensure idempotent, observable, replayable delivery with tenant isolation.

## 2) Proposed high-level components

### 2.1 Internal event production

Domain changes produce internal events (e.g., “company updated”, “signal published”).

Notes:
- Event production should be close to the domain/service boundaries, not in routers.
- For Smart Signals, exports must align with canonical Signals contracts and terminology:
  - `backend/app/signals/audit/README.md`
  - `backend/app/signals/audit/SKILL_signals_intent_system.md`

### 2.2 Integration dispatcher (core)

Responsibilities:
- subscribe to internal events,
- resolve which tenant connections should receive them (routing rules),
- create persistent delivery jobs with idempotency keys.

### 2.3 Delivery workers (retries + rate limiting)

Responsibilities:
- execute delivery attempts (webhook push / partner API calls),
- enforce per-connection throttles,
- retry with backoff,
- quarantine after repeated failures.

### 2.4 Connector/adapters (HubSpot, Pipedrive, generic webhook)

Responsibilities:
- translate canonical integration payloads into vendor-specific APIs/objects,
- handle auth/token refresh (OAuth where applicable),
- normalize errors and retryability signals.

### 2.5 Connection config + secrets + mapping store

Responsibilities:
- store tenant connection configuration and state,
- store partner credentials securely,
- store identity mappings (Queast IDs ↔ partner object IDs),
- store identity match provenance (which strategy matched; confidence; reviewer if needed).

### 2.5a Match review queue (identity safety rail)

Responsibilities:
- show all identity matches (including auto-linked ones),
- allow manual correction/unlink + adding explicit mappings,
- prevent ambiguous/low-confidence inbound events from auto-writing irreversible mappings.

### 2.6 Inbound webhook/API receiver (two-way)

Responsibilities:
- authenticate inbound requests (signatures/tokens),
- validate and normalize inbound event types into canonical internal events,
- ensure idempotency and safe retries,
- persist “ingestion records” for audit and troubleshooting.

## 3) Data flow sketch (outbound)

1) Domain/service emits event `E` (tenant-scoped).
2) Dispatcher resolves enabled connections and creates delivery jobs:
   - stable idempotency keys,
   - payload snapshot,
   - routing metadata.
3) Worker executes delivery via connector (HubSpot/Pipedrive/webhook).
4) Job status is persisted for audit/monitoring.

## 4) Data flow sketch (inbound: company interest highlight)

1) CRM sends inbound event (webhook/API) “company marked as interesting” for tenant connection `C`.
2) Receiver authenticates, validates, and de-dupes.
3) Identity resolution attempts matching (partner ID → domain/email → LinkedIn URL → fuzzy name).
4) Service records tenant “interest” state as a **bookmark** and emits an internal event for downstream effects (optional).
5) Ingestion record persists match outcome + confidence for audit; ambiguous/low-confidence matches are quarantined for review.

## 4) Integration boundaries

- “Integration layer” should not own business rules for Signals; it exports already-computed artifacts.
- Avoid duplicating Signals logic; link to canonical Signals docs and treat exported Smart Signals as Actionable Signals.
