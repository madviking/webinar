Status: draft
Last reviewed: 2026-01-31

# Pipedrive connector — work estimate (v1)

This is a delivery-oriented estimate for a **Pipedrive connector** that integrates Queast’s integration layer with Pipedrive via **OAuth/API token + Webhooks + Pipedrive APIs**, aligned with our current integration-layer decisions:

- Two-way readiness; inbound scope is *light* and becomes a **bookmark** in Queast.
- Outbound payloads are canonical + abstract; per-tenant mapping is supported.
- Exporting informational/legacy signals is **on by default**, but must be explicitly labeled by contract metadata.

## Sources (Pipedrive)

- API basics / auth (API token; OAuth available): https://developers.pipedrive.com/docs/api/v1/
- OAuth 2.0 flow: https://developers.pipedrive.com/docs/api/v1/OAuth-authorization
- Webhooks API: https://developers.pipedrive.com/docs/api/v1/webhooks
- Webhooks v2 guide (payload + retries): https://pipedrive.readme.io/docs/guide-webhooks-v2
- Search API rate limit: https://developers.pipedrive.com/changelog/post/announcing-search-api-rate-limit
- Daily POST/PUT limit: https://developers.pipedrive.com/changelog/post/daily-api-limit-for-postput-endpoints
- Token-based rate limits (and push toward API v2): https://developers.pipedrive.com/changelog/post/breaking-changes-token-based-rate-limits-for-api-requests
- Deprecation of selected API v1 endpoints (effective Jan 1, 2026): https://developers.pipedrive.com/changelog/post/deprecation-of-selected-api-v1-endpoints
- API v2 docs entrypoint: https://developers.pipedrive.com/docs/api/v2/

## Assumptions (what we are building)

**Auth**
- Prefer **OAuth** for multi-tenant installs; support API token as an optional “manual mode” if needed.

**Outbound**
- Organization + person sync (upserts).
- Signal export (Actionable Signals + optional informational/legacy; both include contract metadata).

**Inbound (light)**
- A Pipedrive-side “interest marker” triggers inbound events that create/ensure a **bookmark**.

**Delivery**
- At-least-once with idempotency + retries; persistent delivery logs.

## Pipedrive-specific constraints that affect effort

**API version drift (important)**
- Pipedrive is actively migrating to API v2 and is deprecating selected API v1 endpoints **effective Jan 1, 2026**; deprecated endpoints were only guaranteed through Dec 31, 2025.
- Given today is **2026-01-31**, v1 connector work should treat API v2 as the default for core entities and avoid deprecated v1 endpoints.

**Webhooks v2**
- Webhooks created via API default to **v2** since March 17, 2025.
- Pipedrive considers any **2xx** response as accepted; delivery timeout is **10 seconds**.
- Failed deliveries are retried **3 more times** (after ~3s, ~30s, ~150s).
- If a webhook has no successful deliveries for **3 consecutive days**, it is deleted.
- There is a maximum of **40 webhooks per user**.
- Outgoing webhooks are not subject to API rate limits.

**Rate limits**
- Search endpoints: **10 requests per 2 seconds** per token (`api_token` or OAuth `access_token`).
- Daily fair-usage limit: **10,000 POST/PUT requests per user per day**, reset at midnight UTC.
- Token-based daily budgets exist (429s until reset), and API v2 is encouraged for lower token costs.

## Human-gated prerequisites (Pipedrive)

These are usually quick but can block Codex progress if not ready:

- Create a Pipedrive app (OAuth) and set redirect URLs.
- Decide whether we will support “API token mode” (manual tenant token) in v1.
- Provide Codex with:
  - Pipedrive app client ID/secret,
  - a stable public HTTPS endpoint for inbound webhooks (or a tunnel that can be restarted reliably),
  - and at least one test Pipedrive account to install into.

## Estimation model (Codex-oriented)

We estimate in **Codex Work Units (CWU)**:
- **1 CWU** = a “PR-sized” slice (implementation + tests + docs update), typically spanning a few files.
- **Risk multiplier** reflects expected iteration due to vendor quirks, unclear requirements, or operational hazards.

## Shared integration-layer dependencies (one-time, not Pipedrive-specific)

If not already implemented, see the shared dependency list in:
- `docs/integration_layer/connectors/hubspot/work_estimate.md`

## Pipedrive connector work breakdown (incremental)

| Work package | CWU (range) | Risk | Human gating |
|---|---:|---|---|
| Pipedrive app setup (OAuth config) | 1–3 | Low | Create app + set URLs |
| OAuth install flow (authorize + token exchange + refresh) | 3–6 | Med | Provide app client ID/secret |
| Optional “API token mode” (manual connection) | 1–3 | Low | Tenant supplies token |
| Webhook subscription management (create/delete webhooks) | 2–4 | Med | Decide event types + target URL |
| Webhook receiver (idempotent + retry-aware) | 2–4 | Med | Ensure public HTTPS endpoint |
| Inbound “interest → bookmark” mapping | 2–5 | High | Decide Pipedrive-side marker (label/field/etc.) |
| Identity matching (Pipedrive IDs, domain, LinkedIn URL, fuzzy name) | 3–6 | High | Decide thresholds + review workflow |
| Outbound organization upsert (API v2) | 3–7 | High | Decide field mapping defaults |
| Outbound person upsert (API v2) | 3–7 | High | Decide field mapping defaults |
| Export Signals into Pipedrive objects (notes/activities/custom fields) via mapping | 3–7 | High | Decide default representation |
| Rate-limit/backoff tuning (incl Search 10/2s, daily POST/PUT) | 2–4 | Med | Validate with real tenant plans |
| API v1→v2 alignment work (avoid deprecated v1 endpoints) | 3–8 | High | Depends on chosen endpoints; likely required in 2026 |
| Connector integration tests (sandbox/fixture accounts) | 3–6 | High | Requires real Pipedrive test accounts |
| Ops runbook + support tooling | 1–2 | Low | Health endpoints, diagnostics |

**Pipedrive incremental total:** ~30–69 CWU.

## CWU → “how long does this take with Codex?”

Very rough planning heuristic (assuming credentials + test accounts are ready):
- 4–10 CWU per “focused day” of Codex iteration.
- Pipedrive incremental (~30–69 CWU): ~3–18 focused days.

The long pole is typically:
- API version drift (v1 deprecations vs v2 availability),
- mapping decisions (what objects to use for Signals),
- and identity matching safety (fuzzy matching + review).

## Definition of Done (Pipedrive v1)

- Tenant can connect Pipedrive (OAuth; optionally API token mode); token refresh works.
- Outbound: org/person/signal events are delivered and visible in Pipedrive with contract metadata preserved.
- Inbound: “interest” event creates/ensures a Queast bookmark; ambiguous matches are quarantined for review.
- Delivery logs exist with correlation IDs; backfill can replay safely.
- Webhook receiver handles retries safely (idempotency; attempt metadata).
