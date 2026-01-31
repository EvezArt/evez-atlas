# Entity Propagation Spec

## Access Control Protocol

### Tier Levels & Redaction

| Tier | Label | Response Visibility |
| --- | --- | --- |
| 0 | public | status only |
| 1 | builder | status + builder |
| 2 | admin | status + builder + trace |
| 3 | director | status + builder + trace + metadata |

All awareness and legion status responses MUST redact fields above the caller tier.

### Audit Requirements

Every call to `/resolve-awareness` and `/legion-status` MUST emit an audit entry to `src/memory/audit.jsonl` with:

- timestamp (epoch seconds)
- entity_id
- endpoint
- tier
- result summary payload

### HMAC Signature Verification

Responses from `/resolve-awareness` MUST include a `signature` field. The signature is the HMAC-SHA256 of the redacted response body (excluding the signature) serialized as JSON with sorted keys and compact separators.

Clients MUST verify signatures with the shared `SECRET_KEY` and reject mismatched payloads.

### Rate Limit Specifications

- Tier 0: 10 requests per minute
- Tier 1/2: 50 requests per minute
- Tier 3: 100 requests per minute
# Entity Propagation Specification

## Access Control Protocol

### Tier Levels

| Tier | Name | Access Scope |
| --- | --- | --- |
| 0 | public | Status only |
| 1 | builder | Status + builder entity |
| 2 | admin | Status + builder + trace |
| 3 | director | Status + builder + trace + metadata |

### Redaction Rules

- Tier 0 responses must only include `status` and identifiers.
- Tier 1 responses add `builder` fields.
- Tier 2 responses add `trace` fields.
- Tier 3 responses add `metadata` fields.

### Audit Requirements

- Every call to `/resolve-awareness` or `/legion-status` must be logged.
- Logs are written as JSON lines to `src/memory/audit.jsonl` and include timestamp, entity ID, endpoint, tier, and response payload.

### HMAC Signature Verification

- Responses from `/resolve-awareness` must include a `signature` field.
- The signature is computed as HMAC-SHA256 over the JSON payload (sorted keys, compact separators) using `SECRET_KEY` from the environment.
- Clients must recompute and verify the signature before trusting the response.

### Rate Limit Specifications

- Tier 0: 10 requests per minute.
- Tier 1-2: 50 requests per minute.
- Tier 3: 100 requests per minute.
