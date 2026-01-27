---
name: queast-llm
description: Use when implementing or modifying any LLM-powered feature in Queast (prompt templates in DB + fixtures, LLM usage/cost tracking, and admin drilldowns).
---

# Queast LLM Development

## Using this skill with Codex

Some agents only load “skills” from a configured skills directory. If `queast-llm` is not available as a built-in skill in your session, still follow this document’s workflow; optionally install it into your agent’s skills so it can be auto-applied.

## Non-negotiables

- **Prompts live in DB**: never hardcode system/user prompts in feature code. Fetch prompt text from `service_prompt_templates` via `ServicePromptTemplate` (e.g. `PromptTemplateRepository.get_content(...)`).
- **Prompt defaults + fixtures**:
  - Add a default prompt template name and content so admins can import it (`backend/app/admin_prompts/service.py` `import_missing_defaults()`).
  - Add the prompt to backend test fixtures so tests can run with DB-backed prompts (`backend/fixtures/prompts.py`).
- **LLM usage logging**: record a usage row per call with `LLMUsageService.record_from_response(...)`:
  - Required: `feature_name`, `tenant_id`, `user_id`, `provider`, `model`
  - Optional: `context` (JSON), `prompt_text`/`response_text`
- **Prompt/response storage is admin-controlled**: do not gate capture with env vars. The toggle lives in Admin → LLM Usage and is read from DB settings (`LLMUsageSettingsRepository`).

## Workflow for adding a new LLM feature

1) **Define a canonical `feature_name`** (stable string; do not rename casually).
2) **Add prompt templates**:
   - Choose a template name (e.g. `my_feature_system`, optionally `my_feature_user`).
   - Add defaults to `backend/app/admin_prompts/service.py` so “Import missing” creates them.
   - Add to `backend/fixtures/prompts.py` so tests seed the DB.
3) **Use DB-backed prompts in code**:
   - Fetch via `PromptTemplateRepository(db).get_content(<name>)`.
   - If missing in DB: treat as a configuration error and fall back to deterministic logic (do not silently invent prompts).
4) **Record usage + costs**:
   - After the provider call returns, call `LLMUsageService(db).record_from_response(...)`.
   - Provide `prompt_text` as the serialized provider messages payload and `response_text` as the provider’s raw text output.
5) **Add/extend admin visibility**:
   - Ensure the feature shows up in cost-by-feature aggregation (it will if `feature_name` is set).
   - If you add new dimensions, keep routers thin; add repo/service tests first.
6) **Tests first (no mocks)**:
   - Add failing tests that assert prompt templates are loaded from DB (seeded via fixtures).
   - Add/extend API tests for admin analytics/drilldown if the contract changes.
7) **Housekeeping**:
   - Regenerate OpenAPI types: `cd frontend/ui && npm run generate:api` (or run `openapi-typescript` off `docs/data_backend/openapi.json`).
   - Update `CHANGELOG.md` (dated entry).
   - `cd frontend/ui && npm run build`.

## Reference file(s)

- Prompt fixture seeding: `backend/fixtures/prompts.py`
- Prompt templates model: `backend/app/prompts/models.py`
- Prompt lookup helper: `backend/app/prompts/repository.py`
- Admin prompt defaults import: `backend/app/admin_prompts/service.py`
- Usage logging: `backend/app/llm/usage_service.py`
- Prompt/response toggle storage: `backend/app/llm/settings_repository.py`
- Admin analytics/drilldown: `backend/app/admin_llm_usage/router.py`
