# Runtime Boundary Design Rework Authority 002

Status: AUTHORIZED
Record: RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-REWORK-AUTH-002
Date: 2026-10-27

Exact subject:
bb225507363b22c860e4d5082dd9494160afed77

Independent evaluation:
RLY-S31-DOGFOOD-001-RUNTIME-BOUNDARY-DESIGN-EVAL-002 — REWORK / NARROW

Authorized scope:
1. M002 — correct authority provenance labels so artifact-creation commits and registry-registration commits are distinguished accurately.
2. M003 — define exact immutable identity, canonical content digest, and immutable reference semantics for RuntimePermissionAttestation.

Required provenance:
- design authority artifact creation: 0504263c41d6fa90c726ce0d3c6f2ee789068d6c
- design authority registry registration: 6e177a68f57545d7ce7c4cc451430a35117f6e4c
- M001 rework authority artifact creation: 875520e59b790becec31058dc820da670aa63365
- M001 rework authority registry registration: c3a1e70a6cc43d0360842c79b07e77518562221b

RuntimePermissionAttestation must have:
- stable attestation identity;
- exact canonical SHA-256 content digest;
- immutable ref containing attestation identity and digest;
- exact binding into the final Slice 3.1 ExecutionSubject;
- no inclusion in request_digest_v2, which remains final before this later evidence object.

M001 remains closed. All other Candidate 002 architecture remains frozen.

Authorized output:
one complete Candidate 003 plus registry/document validation.

Successful terminal:
RUNTIME_BOUNDARY_DESIGN_CANDIDATE_003_COMPLETE

Implementation remains unauthorized.
Dogfood 001 remains AUTHORIZED / NOT ADMITTED / NOT CONSUMED.
