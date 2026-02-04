Status: active
Last reviewed: 2026-02-03

# Integration Layer — Implementation Guide (v1)

This guide is for implementers adding a new connector or extending the integration “spine” (contracts, connection management, delivery execution).

## Read first

1) `docs/integration_layer/README.md` (reading order)
2) `docs/integration_layer/04_data_contracts.md` (canonical envelope + event payload minimums)
3) `docs/integration_layer/05_security_and_compliance.md` (threat model + non-negotiables)
4) Backend module READMEs (current code boundaries):
   - `backend/app/integration_layer/README.md` (spine)
   - `backend/app/integration_connections/README.md` (tenant connections + encrypted secrets)
   - `backend/app/integration_connectors/README.md` (vendor adapters)
   - `backend/app/integration_mappings/README.md` (identity mappings + match review queue)

## Current backend boundaries (source-of-truth: code)

We intentionally separate “spine vs connectors” at the module level:

- `app.integration_layer`: vendor-agnostic integration primitives and shared orchestration (health/version now; dispatcher/workers later).
- `app.integration_connections`: tenant-scoped connection rows + encrypted secrets (`service_*` tables only).
- `app.integration_connectors`: partner-specific adapters (auth, HTTP clients, error normalization, mapping).
- `app.integration_mappings`: identity mapping store + match provenance + quarantine/review queue APIs.

Cross-cutting invariants (must hold across all four):
- Multi-tenant safety (no cross-tenant reads/writes).
- Routers are thin; services contain business rules only; repositories contain SQL/ORM only.
- No mocks in tests; use real fixtures + test DB.

## How to add a new connector (checklist)

### 1) Choose a stable `connector_type`

- Use a lowercase, stable identifier (e.g. `hubspot`, `pipedrive`, `webhook`).
- Treat `connector_type` as an externally-visible identifier (API paths, logs, idempotency keys). Don’t rename casually.

### 2) Add/extend connection config + secrets (tenant-safe)

Module: `backend/app/integration_connections/`

- Store **non-secret** config in `ServiceIntegrationConnection.config_json`.
- Store **secrets only** in `service_integration_connection_secrets` (encrypted via `app.shared.crypto.SecretCipher`).
- Never return secrets (plaintext or ciphertext) from any API response schema.

Keep in mind:
- Exactly **one connection per connector type per tenant** (enforced by DB unique constraint).
- Tenant endpoints must remain allowlist gated (see router invariant around `ServiceTenant.integrations_enabled`).

### 3) Implement the connector adapter (vendor-specific)

Module: `backend/app/integration_connectors/`

At minimum, define:
- How the connector authenticates (OAuth vs API token) and which secret keys it expects.
- How it classifies errors (retryable vs non-retryable).
- How it will map canonical envelopes/payloads (from `docs/integration_layer/04_data_contracts.md`) to the vendor’s API.

## Release gate checklist (QA)

Use this checklist before merging/releasing Integration Layer work (connections, identity mappings, delivery logs, proof CLIs, and related UI).

### Required

- Backend tests + coverage (repo root):
  - `source claude_venv/bin/activate && pytest --cov=app --cov-report=term-missing`
  - Requirement: all tests green
  - Requirement: backend coverage ≥ 80% (CI enforces; optionally add `--cov-fail-under=80` locally)
- Frontend build (repo root):
  - `cd frontend/ui && npm run build`
- Docs index / metadata:
  - Any new/renamed `*.md` files are listed in `docs/README.md` (pytest-enforced)
- Changelog:
  - `CHANGELOG.md` updated under **[Unreleased]** for user-facing changes (features/behavior/bugfix/security)

### Required security checks

Verify (via tests preferred) that:

- No integration API response returns plaintext secrets or encrypted secret fields.
- Admin delivery log APIs do not return raw payload bodies:
  - Delivery jobs omit `payload_json`
  - Delivery attempts omit `request_body` and `response_body`
- Proof CLI artifacts do not print or store vendor credentials (e.g., HubSpot access token).

### E2E (required when the UI exists)

When an Integration Layer UI surface is shipped, corresponding Playwright E2E coverage is required before release:

- Tenant Settings → Integrations: connection setup (create/update/disable), allowlist gating, identity review queue actions (with audit note requirement)
- Admin → Integrations: read-only identity review list (and any shipped admin override flows)

Run:

- `cd frontend/ui && npm run test:e2e`

### Recommended (fast signal)

- `source claude_venv/bin/activate && pytest backend/app/integration_connections/tests/ backend/app/integration_deliveries/tests/ backend/tests/unit/test_integration_proof_cli.py`

Security requirements:
- Never log secrets or raw payloads containing PII.
- Prefer logging metadata (event_id, tenant_id, connector_type, request_id, status code, latency).

### CI-friendly Integration Layer suite (no vendor credentials)

Use this for fast, repeatable validation when changing Integration Layer code (connections, spine, deliveries, mappings).

Run (repo root):
```bash
./scripts/qa/run_integration_layer_ci.sh
```

Or equivalent:
```bash
source claude_venv/bin/activate
pytest -q backend/tests/unit/test_docs_index.py backend/tests/unit/test_docs_metadata.py
pytest backend/app/integration_connections/tests \
       backend/app/integration_layer/tests \
       backend/app/integration_deliveries/tests \
       backend/app/integration_mappings/tests \
       backend/tests/unit/test_integration_layer_router_registration.py
```

Optional real-vendor tests (when they exist) should:
- Be skipped by default unless `INTEGRATION_VENDOR_TESTS=1` and credentials are present
- Use sandbox/dev accounts only (never production)
- Perform safe, low-impact operations (prefer read-only checks or deterministic test objects)

### 4) Wire health checks (safe + non-destructive)

The current `/integrations/connections/{connector_type}/health` endpoint returns stored status + “secrets present”.

When adding real connector health checks:
- Keep checks non-destructive and low-risk (e.g., “validate token and fetch identity/owner”).
- Return only redacted diagnostics (no secrets, no PII).

## How to extend contracts / events (v1 additive-only)

Canonical source: `docs/integration_layer/04_data_contracts.md`.

Rules:
- `schema_version` is major-only (`v1`) and must remain **additive-only** within `v1`.
- Event consumers must ignore unknown fields (and ideally unknown event types).
- Every event payload must include a deterministic `data.subject` block and a stable `idempotency_key`.

Signals constraint:
- Exports must not duplicate or redefine Signals logic. Export only already-computed artifacts and treat Smart Signals as Actionable Signals (strict contract metadata required).

## PII policy (person/contact exports)

Decision (v1):
- PII fields are guarded by an explicit allowlist.
- Default allowlist: `work_email` only.
- Not supported/exported in v1: phone numbers, addresses, personal emails.

Connector behavior when email export is disabled:
- If the destination requires email to upsert/create, skip the person export for that event and record a non-retryable failure reason like `blocked_by_pii_policy` (with **no PII** in logs).

## Delivery execution model (when implementing workers)

When implementing dispatcher/delivery workers, follow the DB-backed queue + claim pattern used elsewhere in Queast:

- Persist an outbox event first (immutable, tenant-scoped).
- Create per-connection delivery jobs from the outbox.
- Claim jobs atomically (race-safe), execute connector call, record attempts, retry with backoff, quarantine after repeated failures.

Observability (minimum):
- Correlate `event_id` → `delivery_job_id` → `attempt_id`.
- Store response/request metadata in a redacted form (headers allowlist; body omitted or hashed).

## Required validation commands

Docs-only changes:
- `source claude_venv/bin/activate && pytest -q backend/tests/unit/test_docs_index.py backend/tests/unit/test_docs_metadata.py`

Backend code changes in integration modules (minimum):
- `source claude_venv/bin/activate && pytest backend/app/integration_connections/tests/ backend/tests/unit/test_integration_layer_router_registration.py`

## PR review checklist (non-negotiables)

- Secrets: never returned; never logged; config_json contains no secrets; encrypted-at-rest via `SecretCipher`.
- PII: allowlist enforced; “blocked_by_pii_policy” behavior; no PII in logs.
- Idempotency: deterministic keys; idempotent semantics for inbound; safe retries.
- Retries: retryability classification; backoff; quarantine after cap; no infinite loops.
- Tenant isolation: all queries scoped by tenant; admin endpoints super-admin gated.
- Docs: `docs/README.md` updated with any new `*.md` files; docs-index tests green.
