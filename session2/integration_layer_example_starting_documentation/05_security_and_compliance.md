Status: draft
Last reviewed: 2026-02-01

# Integration Layer — security and compliance (draft)

## 1) Threat model (baseline)

- Credential leakage (OAuth tokens, API keys)
- Cross-tenant data leakage
- Webhook spoofing (fake inbound events) or replay attacks
- Payload exfiltration via logs
- Partner API misuse or over-permissioned scopes

## 2) Outbound webhooks (Queast → tenant destinations)

### 2.1 Signing standard (v1)

We standardize on an HMAC-SHA256 signature over a canonical string:

`{timestamp_unix_seconds}.{raw_request_body_bytes}`

Headers:
- `X-Queast-Timestamp`: unix seconds (UTC)
- `X-Queast-Signature`: `v1=<hex_hmac_sha256>`
- `X-Queast-Signature-Key-Id`: optional key identifier for rotation (string)

Rules:
- `raw_request_body_bytes` is the exact bytes sent on the wire (before any JSON parsing/pretty-printing).
- `hex_hmac_sha256` is `hmac_sha256(secret, canonical_string)` encoded as lowercase hex.
- The signing secret is stored per tenant connection in encrypted secrets (see `backend/app/integration_connections/README.md`).

### 2.2 Verification requirements

Receivers MUST:
1) Reject missing headers (`X-Queast-Timestamp`, `X-Queast-Signature`).
2) Enforce a timestamp window (default: ±5 minutes).
3) Compute the signature over the raw body and compare using constant-time compare.
4) Reject unknown `schema_version` and ignore unknown fields (contract rules in `docs/integration_layer/04_data_contracts.md`).

### 2.3 Replay protection

Receivers SHOULD implement replay protection in addition to the timestamp window.

Recommended strategy (v1):
- Use `event_id` from the envelope (see `docs/integration_layer/04_data_contracts.md`) as the replay key.
- Store `seen:{event_id}` in a TTL cache (Redis) for at least the timestamp window (e.g., 10 minutes).
- If `event_id` was seen before, treat as a replay and reject (or accept-but-no-op if the receiver supports idempotent semantics).

### 2.4 Key rotation

We support rotation by allowing multiple valid secrets per connection:
- “active” signing key (used for outbound signing)
- “previous” key (accepted for verification during a transition window)

If a destination supports it, we MAY include `X-Queast-Signature-Key-Id` so receivers can select the right secret. Receivers must still be able to fall back to trying all configured keys.

### 2.5 Logging and payload handling

- Never log: signing secrets, OAuth tokens, raw request bodies, or any PII fields.
- Prefer logging: `event_id`, `tenant_id`, `integration.connection_id`, `event_type`, `trace.correlation_id`, request size, response status, latency.
- If you must persist payload snapshots for debugging/audit, treat them as sensitive: encrypt at rest, minimize retention, and ensure access is admin-only.

## 3) Partner API connections (HubSpot/Pipedrive)

- Prefer OAuth where feasible; store refresh/access tokens encrypted.
- Scope minimization: request only what is required for the chosen export mechanism.
- Token rotation and revocation must be reflected in connection health status.

## 4) Inbound webhooks (partner/tenant systems → Queast)

Inbound endpoints MUST:
- Authenticate requests (partner-specific signatures for HubSpot/Pipedrive; HMAC for generic webhook integrations).
- Be idempotent by `idempotency_key` (see `docs/integration_layer/04_data_contracts.md`) and never implement “toggle” semantics for webhook-triggered actions.
- Enforce tenant isolation based on the resolved `connection_id` (no cross-tenant writes).

## 5) PII handling

- Person exports must have an explicit policy for which fields are allowed (email, phone, etc.).
- Provide a tenant-level configuration guardrail for PII export.

In v1:
- Default allowlist is `work_email` only (see `docs/integration_layer/07_implementation_guide.md`).
- Any “payload contains PII” state should be represented via the envelope `privacy` metadata (safe-to-log only), not by logging the PII itself.

## 6) Implementer checklist (minimum)

- Signing: `X-Queast-Timestamp` + `X-Queast-Signature` present, verified, and timestamp window enforced.
- Replay: `event_id` de-duped via Redis TTL key (or receiver-provided idempotency).
- Redaction: no secrets/PII in logs; store only hashes/sizes when debugging.
- Tenant safety: connection resolution is tenant-scoped; no cross-tenant reads/writes.
