Status: active
Last reviewed: 2026-01-31

# Unified Agent Guide (CLAUDE + AGENTS)
This single guide is the authoritative reference for all agents (Claude Code and others). It is intentionally concise and links to detailed docs.

## Read This First

- Documentation: read `docs/README.md` (index) and `docs/documentation-standards.md` before creating/updating docs.
- Backend work: read `docs/howto/crud.md`, `docs/development-flow.md`, `docs/testing/README.md` (backend), `docs/code-review.md`, `docs/metadata-management.md`.
- Frontend work: read `frontend/ui/README.md`, `docs/testing/README.md` (frontend + E2E), `docs/howto/crud.md` (frontend section), `docs/code-review.md`.
- Features: check `docs/features/` for module specifics before coding.
- CLI commands (proof + management): `docs/cli/README.md` (single authoritative list)
- LLM work: follow `.codex/skills/queast-llm/SKILL.md` strictly (DB-backed prompts + fixtures + usage tracking). If your agent supports “skills”, install `queast-llm` so it can be auto-applied.
- Signals Lab analyze/refactors: follow `.codex/skills/signals-lab-proof/SKILL.md` (proof-of-work CLI output is required).
- Signals system (terminology + architecture): follow `.codex/skills/signals-intent-system/SKILL.md` strictly. If your agent supports “skills”, install it by copying `.codex/skills/signals-intent-system/` to `~/.codex/skills/signals-intent-system/` and restart Codex.

## Non‑Negotiables

- Virtualenv: always `source claude_venv/bin/activate` before any backend work.
- TDD flow: baseline tests → write failing tests first → minimal code → all tests green → update `CHANGELOG.md` → final full suite. Never report completion without green tests.
- No mocking: use real fixtures and test database; no production mock imports.
- Caching: use Redis for ephemeral caches (not database tables/migrations). Prefer TTL-based keys with versioned namespaces; add integration tests that use a real Redis instance when available. See `docs/caching-to-redis.md`.
- LLM usage tracking: instrument every LLM call with `app.llm.usage_service.LLMUsageService` and pass `feature_name`, `tenant_id`, `user_id`, `provider`, `model` (plus optional `context`; optional prompt/response capture is toggled in Admin → LLM Usage).
- Separation of concerns: models (business methods), services (business rules, no SQL), repositories (data access only), routers (thin HTTP only). No SQL in services/routers.
- CRUD base: use `backend/app/core/crud_base.py` with repositories extending `backend/app/shared/repositories/base.py`.
- Model‑first: add/extend domain models with behavior before wiring endpoints.
- OpenAPI types: generate and use `frontend/ui/src/generated/openapi.ts` for API contracts. Do not duplicate request/response types.
- Changelog: update `CHANGELOG.md` for any user‑facing, behavior, schema, endpoint, security, bugfix, or feature change. Timestamp them using system time.
- Database tables: `service_*` are app-owned; `data_*` are maintained by another system and must be treated as read-only.
- Change in database model: ALWAYS create a migration. 
- When you start to work on a module, first check whether it has a README.md and read that
- If you make changes in any FE files, before saying "I'm ready", run npm run build to make sure everything compiles. Run lint if you consider it will also be needed.
- Absolutely no GIT operations like reset and checkout. Only for seeing history. Human operator handles all git operations unless otherwise directly instructed. 

## Communicating with the user & documenting

- Always ask questions if something is not clear / leaves room for interpretation. Try to clarify in the beginning of the session, rather than stopping to ask questions all the time.
- Always use numbered lists for questions to make it easier to answer.
- Any bigger plan should always first be recorded as an md-planning file inside docs/ - and you should keep progress tracking in that file
- What ever might be relevant for next developers should be documented primarily in README.md files and if needed to separate files. These need to be always within the module.
- When adding/renaming Markdown docs, keep them discoverable by ensuring they’re covered by the `docs/README.md` index (pytest enforces this).
- For cross-cutting docs under `docs/`, include `Status:` and `Last reviewed:` near the top (pytest enforces this).
- When documenting cross-cutting, agent-facing “must-follow” truths, explicitly consider whether it should be a Codex skill under `.codex/skills/` (and link it from `docs/README.md`).
- Prefer deleting obsolete progress docs; if keeping a deprecated doc, mark it `Status: deprecated`, add `Superseded by: ...`, and move it to `docs/deprecated/` (or `docs/planning/retired/` for planning docs).

## Quick Commands

- Backend baseline: `source claude_venv/bin/activate && pytest --cov=app --cov-report=term-missing`
- Frontend baseline: `cd frontend/ui && npm run test:coverage && npm run test:e2e`
- Implement → verify: rerun the same; ensure coverage ≥ thresholds (backend ≥80%).
- Lint (FE): `cd frontend/ui && npm run lint`
- Dev servers: backend `uvicorn app.main:app --reload --port 8099`; frontend `cd frontend/ui && npm run dev` (port 6565).
- Generate API types: `cd frontend/ui && npm run generate:api` after backend schema/route changes.

## Management CLI

- Canonical command list + explanations (proof vs management): `docs/cli/README.md`
- Run from repo root:
  - `source claude_venv/bin/activate && python cli.py --help`
- Naming convention:
  - `*-proof` command groups are proof-of-work CLIs (stable JSON artifacts; used for refactor verification).
  - everything else is management/ops (may write to DB; check `--help`).

## Backend Structure (strict SoC)

Each module mirrors:
```
backend/app/
├── <module>/
│   ├── models.py      # Rich domain models (business methods)
│   ├── service.py     # Business logic only (no SQL)
│   ├── repository.py  # Data access only
│   └── router.py      # Thin HTTP endpoints
├── core/
│   ├── crud_base.py   # Generic BaseService
│   └── dependencies.py
└── shared/repositories/base.py  # BaseRepository
```
Rules:
- Services use repositories; repositories may use SQL/ORM only.
- Validation and permissions live in models/services, not routers.

## Testing Setups

- Backend (pytest):
  - Commands: `pytest`, `pytest tests/api/`, `pytest tests/unit/`, `pytest tests/integration/`, `pytest --cov=app --cov-fail-under=80`.
  - Fixtures: use real test DB and provided fixtures; no mocks.
- Frontend (Vitest):
  - Commands: `npm test`, `npm run test:run`, `npm run test:ui`, `npm run test:coverage`.
- E2E (Playwright):
  - Commands: `npm run test:e2e`, `npm run test:e2e:ui`, `npm run test:e2e:headed`, `npm run test:e2e:comprehensive`.
  - Architecture and fixtures are documented in `docs/testing/README.md`.

## Frontend Principles

- Types: single source of truth in `src/generated/openapi.ts` for API and `src/shared/types/` for domain/common types. Do not re‑define.
- State: use React Query for server state; no business rules in components.
- Styling: Radix UI + Tailwind; avoid custom directives unless justified.
- Paths: use `@/` alias for `./src/`.
- We try to load data for any page with as few calls as possible. So if we have a list, this should come from one api call and preferably also one SQL query

## Checklist Before You Say “Done”

- Tests first, then code; all tests passing (BE + FE + E2E as applicable).
- Coverage maintained or improved (≥80% backend; frontend per project standards).
- Signals Lab work: proof CLI produces valid JSON with `llm_used=true` (`python cli.py signals-lab-proof analyze-job ...`; see `docs/cli/README.md`).
- No mocks used; no production mock imports.
- Separation of concerns respected (models/services/repositories/routers).
- OpenAPI types regenerated if backend contracts changed; FE updated accordingly.
- `CHANGELOG.md` updated under [Unreleased].
- Frontend builds
- Frontend lints (not strictly required in all cases)

## Where To Find Details

- CRUD patterns and base services: `docs/howto/crud.md`.
- Full testing strategy and E2E framework: `docs/testing/README.md`.
- Development workflow: `docs/development-flow.md`.
- Code review expectations: `docs/code-review.md`.
- Metadata system: `docs/metadata-management.md`.
- Feature specifics: `docs/features/`.

Ports: backend 8099, frontend dev 6565. DB config lives in `.env`. Tables: `service_*` (owned), `data_*` (external, read-only).
