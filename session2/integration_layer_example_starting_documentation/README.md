Status: draft
Last reviewed: 2026-02-03

# Integration Layer (HubSpot + Pipedrive) — docs

This folder contains the cross-cutting documentation for Queast’s **integration layer**: how Queast exchanges data with external systems (starting with HubSpot and Pipedrive) in a **tenant-safe, auditable, versioned** way.

## Scope (initial)

- Outbound delivery to tenant-connected systems via **webhooks and/or partner APIs**
- Objects: **companies**, **people**, **Smart Signals** (Actionable Signals; strict-only), and possibly **job ads** as evidence references/links
- Multi-tenant installation/config, auth, delivery guarantees, retries, and observability

Non-goals (for now):
- Building a general “iPaaS” or workflow engine
- Supporting every CRM; initial focus is HubSpot + Pipedrive
- Re-defining Signals terminology or contracts (link to canonical Signals docs instead)

## Reading order

1) `docs/integration_layer/00_executive_summary.md`
2) `docs/integration_layer/01_requirements.md`
3) `docs/integration_layer/02_open_questions.md`
4) `docs/integration_layer/03_architecture_overview.md`
5) `docs/integration_layer/04_data_contracts.md`
6) `docs/integration_layer/05_security_and_compliance.md`
7) `docs/integration_layer/06_phases_and_mvp.md`
8) `docs/integration_layer/07_implementation_guide.md`
9) `docs/integration_layer/connectors/hubspot/work_estimate.md`
10) `docs/integration_layer/connectors/pipedrive/work_estimate.md`

## Planning/progress

- Archived plan: `docs/planning/retired/2026-01-31-integration-layer-plan.md`

## Canonical references (do not drift)

- Signals terminology + invariants:
  - `backend/app/signals/audit/README.md`
  - `backend/app/signals/audit/SKILL_signals_intent_system.md`
- Signals system docs (implementation-aligned):
  - `backend/app/signals/docs/README.md`

Integration implementation workflow (Codex skill):
- `.codex/skills/integration-layer/SKILL.md`
