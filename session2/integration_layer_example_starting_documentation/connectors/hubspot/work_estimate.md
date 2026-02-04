Status: draft
Last reviewed: 2026-01-31

# HubSpot connector — work estimate (v1)

This is a delivery-oriented estimate for a **HubSpot connector** that integrates Queast’s integration layer with HubSpot via **OAuth + Webhooks + CRM APIs**, aligned with our current integration-layer decisions:

- Two-way readiness; inbound scope is *light* and becomes a **bookmark** in Queast.
- Outbound payloads are canonical + abstract; per-tenant mapping is supported.
- Exporting informational/legacy signals is **on by default**, but must be explicitly labeled by contract metadata.

## Sources (HubSpot)

- App auth types (OAuth vs static): https://developers.hubspot.com/docs/apps/developer-platform/build-apps/authentication/overview
- App creation (developer platform 2025.2): https://developers.hubspot.com/docs/apps/developer-platform/build-apps/create-an-app
- Webhooks API guide: https://developers.hubspot.com/docs/api/webhooks
- Validate webhook requests (signature v3): https://developers.hubspot.com/docs/api/webhooks/validating-requests
- Webhook signatures v3: https://developers.hubspot.com/changelog/introducing-version-3-of-webhook-signatures
- API usage limits: https://developers.hubspot.com/docs/developer-tooling/platform/usage-guidelines

## Assumptions (what we are building)

**Auth**
- Use **OAuth** (required for multi-account installs).
- Token storage is per-tenant connection; refresh tokens supported.

**Outbound**
- Company + person sync (upserts).
- Signal export (Actionable Signals + optional informational/legacy; both include contract metadata).

**Inbound (light)**
- A HubSpot-side “interest marker” (exact mechanism TBD) triggers inbound events that create/ensure a **bookmark**.

**Delivery**
- At-least-once with idempotency + retries; persistent delivery logs.

## HubSpot-specific constraints that affect effort

**Rate limits**
- For **OAuth apps distributed via HubSpot Marketplace**, each installed HubSpot account is limited to **110 requests per 10 seconds** (excluding CRM Search API).
- For **privately distributed apps**, HubSpot enforces:
  - per-app burst limits (per 10 seconds) that vary by account tier,
  - and daily request limits shared across the HubSpot account (across all apps).
- CRM Search API: separate limit of **5 requests/second per account**, plus additional constraints (result window cap; reduced rate-limit header behavior).

**Webhooks**
- Webhook request validation:
  - OAuth apps can validate with `X-HubSpot-Signature-v3` + `X-HubSpot-Request-Timestamp` using HMAC SHA-256.
  - Requests older than **5 minutes** should be rejected (replay protection).
- Delivery shape/behavior:
  - HubSpot sends webhook events in batches (up to **100 events per request**).
  - HubSpot can send up to **10 concurrent webhook requests**.
  - Target must respond within **5 seconds**; non-2xx, timeouts, and connection failures are retried.
  - HubSpot retries webhook deliveries up to **10 times** spread over ~24 hours (with jitter).
  - Webhook requests do **not** count against HubSpot API rate limits.
- Scale limits: up to **1,000 webhook subscriptions per app**.

## Estimation model (Codex-oriented)

We estimate in **Codex Work Units (CWU)**:
- **1 CWU** = a “PR-sized” slice (implementation + tests + docs update), typically spanning a few files.
- **Risk multiplier** reflects expected iteration due to vendor quirks, unclear requirements, or operational hazards.

Calendar time depends heavily on:
- availability of test accounts + credentials,
- network/env readiness,
- external app review/approval (if marketplace listing is required),
- and “human gate” tasks (creating apps, installing to test portals, setting up secure inbound URLs).

## Human-gated prerequisites (HubSpot)

These are usually quick but can block Codex progress if not ready:

- Create a HubSpot **developer account** and a test HubSpot portal.
- Create the app and set:
  - OAuth redirect URLs,
  - required scopes,
  - webhook target URL(s),
  - and (if applicable) Marketplace distribution settings.
- Provide Codex with:
  - HubSpot app client ID/secret,
  - a stable public HTTPS endpoint for inbound webhooks (or a tunnel that can be restarted reliably),
  - and a test tenant/portal to install into.

## Shared integration-layer dependencies (one-time, not HubSpot-specific)

These are prerequisites to any CRM connector; if they’re not already implemented, add them once:

| Work package | CWU (range) | Risk | Notes |
|---|---:|---|---|
| Connection model + secrets storage | 3–6 | Med | Per-tenant connections; encrypted credentials |
| Canonical outbound event envelope + schemas | 2–4 | Low | Versioning + idempotency keys |
| Delivery jobs, retries, DLQ/quarantine, logs | 6–10 | Med | At-least-once, visibility, replay safety |
| Backfill/replay framework | 3–6 | Med | “Export last N days” + throttling |
| Mapping framework (tenant-specific) | 6–12 | High | Abstract mapping to CRM objects/fields |
| Inbound ingestion framework + match review queue | 5–9 | High | Auto-link above threshold + review all matches |
| Observability (metrics + admin views) | 2–5 | Med | Per-connection health + last error |

**Shared total:** ~27–52 CWU (one-time).

## HubSpot connector work breakdown (incremental)

| Work package | CWU (range) | Risk | Human gating |
|---|---:|---|---|
| HubSpot app setup (OAuth config, scopes, redirect URLs) | 1–3 | Low | Create app + set URLs |
| OAuth install flow (authorize + token exchange + refresh) | 3–6 | Med | Provide app client ID/secret |
| Token storage + rotation strategy | 1–3 | Med | Security review |
| Webhook subscription management | 2–4 | Med | Decide event types + target URL |
| Webhook receiver: signature v3 validation + replay protection | 2–5 | Med | Ensure public HTTPS endpoint |
| Inbound “interest → bookmark” mapping | 2–5 | High | Decide HubSpot-side marker (property/label/etc.) |
| Identity matching (HubSpot IDs, domain, LinkedIn URL, fuzzy name) | 3–6 | High | Decide thresholds + review workflow |
| Outbound company upsert (properties + upsert rules) | 3–6 | Med | Decide field mapping defaults |
| Outbound person upsert (contacts) | 3–6 | Med | Decide field mapping defaults |
| Export Signals into HubSpot objects (notes/tasks/custom object) via mapping | 3–7 | High | Decide default representation |
| Rate-limit/backoff tuning (burst + daily + search) + batching | 2–5 | Med | Validate with real account limits |
| Connector integration tests (sandbox/fixture accounts) | 3–6 | High | Requires real HubSpot test portal(s) |
| Ops runbook + support tooling | 1–2 | Low | Health endpoints, diagnostics |

**HubSpot incremental total:** ~28–65 CWU.

## CWU → “how long does this take with Codex?”

Very rough planning heuristic (assuming credentials + test portals are ready):
- 4–10 CWU per “focused day” of Codex iteration.
- HubSpot incremental (~28–65 CWU): ~3–16 focused days.

The long pole is typically not implementation speed; it’s:
- getting app + scopes configured correctly,
- validating webhook signature behavior against real traffic,
- and deciding default mappings that tenants can override safely.

## Definition of Done (HubSpot v1)

- Tenant can connect HubSpot via OAuth; token refresh works.
- Outbound: companies/people/signal events are delivered and visible in HubSpot with contract metadata preserved.
- Inbound: “interest” event creates/ensures a Queast bookmark; ambiguous matches are quarantined for review.
- Delivery logs exist with correlation IDs; backfill can replay safely.
- Webhook requests are validated (signature v3 + timestamp window).
