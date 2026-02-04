Status: draft
Last reviewed: 2026-01-31

# Integration Layer — phases and MVP (draft)

This document proposes an incremental rollout that keeps the integration layer **abstract**, vendor-agnostic, and tenant-safe, while allowing HubSpot/Pipedrive connectors to evolve without breaking contracts.

## Phase 0 — Canonical contracts + outbound webhooks (foundation)

- Define canonical event envelope + versioning (`schema_version`, idempotency keys).
- Implement persistent delivery jobs + retries + logs.
- Provide generic tenant webhooks as the first delivery target.
- Provide a backfill mechanism for outbound events.

Outcome: a stable integration “spine” that other connectors can reuse.

## Phase 1 — HubSpot + Pipedrive outbound connectors (vendor adapters)

- Add HubSpot connector with a minimal, opinionated default mapping (configurable).
- Add Pipedrive connector with a minimal, opinionated default mapping (configurable).
- Add per-tenant mapping overrides (field mapping + object type mapping) within guardrails.

Outcome: first-class CRM connectors without changing the canonical payloads.

## Phase 2 — Inbound “company interest highlight” (light two-way)

- Add inbound receiver paths (webhook/API) per vendor as needed.
- Translate inbound “interest” to a canonical internal event.
- Implement identity resolution with:
  - auto-link above threshold,
  - quarantine for ambiguity,
  - and a match review queue that lists all matches (including auto-linked) for correction.
- Record the inbound result as a **bookmark**.

Outcome: two-way begins without expanding into full CRM sync.

## Phase 3 — Bidirectional enrichment (optional / future)

- Expand inbound to support richer updates (e.g., CRM owner changes, pipeline stage changes) only if required by product.
- Add reconciliation/backfill in both directions with explicit conflict policies.

Outcome: full “sync” capability if/when product needs it.
