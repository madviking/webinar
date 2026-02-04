Status: draft
Last reviewed: 2026-01-31

# Integration Layer — open questions

## 1) Scope & delivery mode

1) Inbound scope is “company interest highlights” — v1 decision: this creates a **bookmark**.
2) Do we treat inbound “bookmark” as:
   - idempotent “ensure bookmarked”, or
   - a “toggle” action (not recommended for webhooks)?
2) Should we support both:
   - generic tenant webhooks, and
   - native CRM app/connectors (HubSpot/Pipedrive APIs)?
3) Is the primary intent:
   - “keep CRM in sync with Queast entities”, or
   - “notify CRM users about Signals”, or both?

## 2) Objects & payload shape

1) What is the minimum payload for:
   - company, person, signal, job ad reference?
2) Should Smart Signals be exported as:
   - notes/activities,
   - tasks,
   - custom objects,
   - or as a canonical webhook event only (tenant/connector builds mapping)?
3) Do we export only **strict** Smart Signals (tenant `/signals` contract), or do we ever export informational/legacy types to CRMs?
   - v1 decision: export **strict-only** (Actionable Signals) unless/until a separate, explicit informational export mode is approved.
   - What are the default destination behaviors per CRM (notes vs tasks vs custom objects), and what are the tenant override guardrails?

## 3) Identity & mapping

1) What is the expected matching strategy for company/person (domain, email, external IDs)?
2) How should fuzzy company-name matching behave?
   - v1 decision: auto-link above threshold + a place to manually review all matches.
3) What should the default threshold be, and what safety rails prevent “wrong merges” from poisoning the mapping store?
3) Do we allow tenant override rules for matching (e.g., “prefer domain match”, “prefer LinkedIn URL”)?
4) Where do we store partner IDs and mapping provenance (per-connection mapping table vs metadata fields)?

## 4) Lifecycle & replay

1) Which events should trigger exports (create/update/delete)?
2) How do we handle “signal cooled off” or “suppressed” states in external systems:
   - do we retract, update, or only append new events?
3) Do we need a tenant-facing “replay last N days” control, and what are the guardrails?

## 5) Permissions & product ownership

1) Who configures integrations?
   - v1 decision: **tenant_admin-only** (tenant-wide), with **admin** capability for bootstrap/override/support.
2) Are exports scoped to a tenant’s entire dataset, or to subsets (e.g., bookmarked companies only)?
   - v1 default decision: **tenant-wide** export scope (with later scoping controls as needed).
3) Do we need per-object opt-outs (e.g., do-not-export flags)?

## 6) Security & compliance

1) Which signing/encryption approach do we standardize on for generic webhooks?
2) Do we store outbound payloads (for audit/debug), and if so:
   - for how long,
   - and are they encrypted at rest?
3) What PII policy applies to person exports (email, phone, etc.)?
4) For inbound events: do we require signed webhooks only, or also IP allowlists?
