# Relay Dogfood 001 — Request Recovery Record

**Record:** `RLY-S31-DOGFOOD-001-REQUEST-RECOVERY-001`

**Disposition:** `ABANDONED_PREAUTH_PREPARATION`

This record documents abandonment of the first preparation-only
`ProjectStateRequest`. Its exact schema-v1 payload was not durably preserved.
The digest is not sufficient to recover the missing fields or establish the
exact request identity. No digest-preimage reconstruction or field inference
was performed.

| Old request field | Exact value |
| --- | --- |
| `request_key` | `dogfood-001-2b87f1e4-4185-4ed8-9ac8-a900804b59cd` |
| Digest | `sha256:8296eeb566c9341d82be1435114d8cdcbd3dd58e135835f25586d591b83d4b13` |
| `intended_attempt_id` | `exec-2b87f1e4-4185-4ed8-9ac8-a900804b59cd` |

Reason: the complete serialized `ProjectStateRequest` payload was not
durably retained. The exact ActorRef, subject dimensions, and other request
fields cannot be established from the digest alone. This request is not an
authority basis for a later execution.

The preparation record was pre-authority. No execution or governance resource
was consumed:

| Resource/action | Result |
| --- | --- |
| Human grant issued | No |
| Reservation created | No |
| WorkPacket created | No |
| WorkspacePlan created | No |
| Runtime session created | No |
| Prompt admitted | No |
| Provider/model call | No |
| Execution attempt consumed | No |

This is historical evidence only. It does not supersede an issued authority;
none existed. Any replacement request and intended-attempt identity must be
new, complete, durably serialized, and independently digested before Human
pre-execution acceptance.
