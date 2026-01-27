# CMS Admin Module

Admin-only CRUD for managing simple HTML content blocks and email templates.

## Structure
- `models.py`: `ServiceContentBlock`, `ServiceEmailTemplate`
- `repository.py`: data access via `BaseRepository`
- `service.py`: business validation with `BaseService`, variables catalog
- `schemas.py`: Pydantic DTOs for create/update/response
- `router.py`: super_admin HTTP endpoints under `/api/v1/admin/cms`
- `seeds/`: file-backed defaults used by `import-missing` seed endpoints

## API
- Content Blocks
  - Blocks include a `category` (default `content`). `product_tour` is used for Shepherd tour JSON (default `signal_scoring_tour` lives there).
  - `GET /admin/cms/blocks` list
  - `GET /admin/cms/blocks/{id}` get one
  - `POST /admin/cms/blocks` create
  - `PUT /admin/cms/blocks/{id}` update
  - `DELETE /admin/cms/blocks/{id}` delete
- Email Templates
  - `GET /admin/cms/email-templates?skip&limit&search` list
  - `POST /admin/cms/email-templates` create
  - `PUT /admin/cms/email-templates/{id}` update
  - `DELETE /admin/cms/email-templates/{id}` delete
  - `POST /admin/cms/email-templates/load-defaults` seed default invitation template
  - `POST /admin/cms/email-templates/import-missing` seed defaults for all standard templates (invitation, daily_digest, password_reset, usage_alert)
- Variables
  - `GET /admin/cms/variables` list supported placeholders per category

- Notification Templates (email + slack)
  - `GET /admin/cms/notification-templates?template_type&category` list
  - `POST /admin/cms/notification-templates` create
  - `PUT /admin/cms/notification-templates/{id}` update
  - `DELETE /admin/cms/notification-templates/{id}` delete
  - `POST /admin/cms/notification-templates/import-missing` seed baseline notification templates if missing

Access: `super_admin` role only.
