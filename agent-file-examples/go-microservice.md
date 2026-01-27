# MDS Service — Developer Guide (v6, GORM‑Driven)

Overview
- Tech stack: Go (Fiber), GORM (MySQL), optional BigQuery.
- Schema source of truth: GORM models in `internal/models`. Migrations run via AutoMigrate.
- Dynamic table APIs: Implemented over GORM (no SQLBoiler).

Schema Management (MySQL)
- Canonical models live in `internal/models`. To change schema:
  1) Edit the relevant GORM model(s) and tags.
  2) Run migrations: `make migrate` (or `RUN_MIGRATIONS=true` through Docker).
  3) If the API should expose new fields, update API structs under `internal/database` as needed.
- Notes:
  - SQLBoiler and schema‑cli SQL generation are deprecated and removed in v6.
  - AutoMigrate applies additive and non‑destructive changes; be cautious with renames or type changes.

BigQuery
- BQ dataset/tables are created/updated via code in `internal/database/bigquery/` if BQ is configured.
- Configure: `BIGQUERY_PROJECT_ID`, `BIGQUERY_DATASET`, optional `BIGQUERY_CREDENTIALS`.
- Run with: `make migrate` (BQ migrations are conditional on env).

Dynamic Table Endpoints (GORM)
- Purpose: internal/admin CRUD access to whitelisted tables with search/filter/sort.
- Routes (protected by API key):
  - GET `/api/v1/tables/:table` — list with `limit`, `offset`, `search`, `order`, `sort` + filter fields
  - POST `/api/v1/tables/:table` — create
  - GET `/api/v1/tables/:table/:id` — get by ID
  - PUT/PATCH `/api/v1/tables/:table/:id` — update by ID
  - DELETE `/api/v1/tables/:table/:id` — delete by ID
- Config: YAML parsed by `internal/config/table_config.go`. Defines table name, permissions, pagination defaults, searchable/filterable/sortable fields.
- Implementation: `internal/api/handlers/dynamic_gorm.go` and routes from `internal/api/dynamic_routes.go`.

Migrations & Running
- Local: `make migrate` then start the server (`cmd/server/main.go`).
- Docker Compose: migrations run automatically before the server when enabled.
- Env vars: `DB_HOST`, `DB_PORT`, `DB_USER`, `DB_PASSWORD`, `DB_NAME`, optional `DB_JOB_ADS` for job ads DB.

Development Rules
- Always update GORM models first; let AutoMigrate materialize schema changes.
- Keep API structs aligned to what the API returns (under `internal/database`).
- Avoid manual SQL migrations; do not reintroduce SQLBoiler.
- Always update CHANGELOG

Testing
- Unit tests focus on handler logic and mappings.
- Integration/E2E tests cover DB interactions (MySQL) and, if configured, BigQuery.

See also: `docs/schema/adding-columns.md` for a concise checklist to add new fields across MySQL, API structs, and BigQuery.
Recipe: `docs/recipes/adding-company-columns/README.md` for the step-by-step `data_companies` flow (models, MySQL upsert, BigQuery, Swagger).

Documentation
- Start with `docs/index.md` for an up-to-date map of documents. Please read this index before making any changes.

Updating API endpoints:
- Always update swagger documentation fully
