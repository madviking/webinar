Status: draft
Last reviewed: 2026-01-31

# Integration Layer — executive summary (management)

## What we’re building

We are building an **integration layer** so tenants can connect their CRM (starting with **HubSpot** and **Pipedrive**) and receive Queast data in their existing workflow.

In v1 we support:
- **Outbound sync/notifications** to CRM (companies, people, Smart Signals).
- **Light inbound** from CRM into Queast: a CRM “company is interesting” event creates/ensures a **bookmark** in Queast (two-way readiness).

## Why it matters

- Tenants live in their CRM; integrations reduce friction and increase adoption.
- Integrations enable “signals → action” by delivering recommendations where teams already work.
- Two-way (even if light inbound) prevents Queast from being a one-way dashboard and enables feedback loops (e.g., “this company matters”).

## What’s in scope for the first two connectors

**Shared foundation (built once, reused by all connectors)**
- Tenant-safe connection setup (per-tenant credentials/config)
- Delivery pipeline: retries, idempotency, logs, backfill/replay
- Mapping framework: connector-specific defaults + tenant overrides
- Identity matching: multiple strategies (IDs, domain/email, LinkedIn URLs, fuzzy name matching) plus a review queue

**Connector-specific work (built per CRM)**
- OAuth + token refresh (preferred for SaaS installs)
- CRM-specific API adapters (company/org, person/contact, exporting Signals to CRM objects)
- Webhook subscriptions + inbound receiver (for “interest → bookmark”)
- Rate limit handling and vendor quirks

## Effort estimate (Codex-oriented)

We estimate in **Codex Work Units (CWU)**:
- 1 CWU ≈ a small PR-sized slice (implementation + tests + docs update)
- Typical throughput (once unblocked): **~4–10 CWU per focused day**

**Shared foundation (one-time):** ~27–52 CWU  
**HubSpot connector (incremental):** ~28–65 CWU (`docs/integration_layer/connectors/hubspot/work_estimate.md`)  
**Pipedrive connector (incremental):** ~30–69 CWU (`docs/integration_layer/connectors/pipedrive/work_estimate.md`)

**Total for “foundation + HubSpot + Pipedrive”:** ~85–186 CWU  
Roughly **~9–46 focused days** of Codex iteration (depends heavily on decisions + vendor setup).

## Primary risks and what management can do to reduce them

1) **Mapping decisions (how Signals appear in CRMs)**
   - Risk: rework if we pick the wrong “default” representation (note vs task vs custom object).
   - Mitigation: pick an MVP default per CRM + keep tenant override mapping from day 1.

2) **Identity matching correctness (fuzzy name matching)**
   - Risk: wrong matches cause data pollution in CRM and loss of trust.
   - Mitigation: auto-link only above threshold + a review queue listing *all* matches (including auto-linked) for correction.

3) **Pipedrive API version drift**
   - Risk: API v1 endpoint deprecations increase churn.
   - Mitigation: implement against API v2 where possible and treat v1 as legacy.

4) **Human-gated vendor setup**
   - Risk: Codex work blocks if test accounts, apps, credentials, or webhook endpoints are not ready.
   - Mitigation: prepare vendor apps + test installs early (see next section).

## Human-gated prerequisites (must be ready early)

- HubSpot: developer account + app created, OAuth redirect URLs set, test portal to install into, webhook URL reachable.
- Pipedrive: app created (OAuth), test account(s), webhook URL reachable.
- A stable public HTTPS endpoint (or a reliably restartable tunnel) for inbound webhooks.
- Product decisions on:
  - default export scope (we assume “all” by default),
  - default mapping (per CRM),
  - and the initial fuzzy-match threshold.

## Recommended rollout (phased)

1) **Phase 0 (foundation):** delivery pipeline + backfill + logs + mapping + identity review queue  
2) **Phase 1 (outbound):** HubSpot + Pipedrive outbound sync (companies/people/signals)  
3) **Phase 2 (inbound light):** inbound “interest → bookmark” for both CRMs  

This sequencing reduces risk: we get value quickly from outbound while building the safety rails needed for two-way.

