# Relay — Slice 2.1 Provider Environment Sidecar Run 007 Handoff

**Document class:** Immutable execution handoff
**Status:** IMMUTABLE
**Date:** 2026-10-07
**Record:** `RLY-S21-SIDECAR-PROVIDER-HANDOFF-006`

## Authority and subject

- Sidecar authority: `RLY-S21-SIDECAR-AUTH-001 — AUTHORIZED`
- V2 provisioning authority: `RLY-S21-SIDECAR-V2-PROVISION-AUTH-001 — AUTHORIZED`
- Run-006 evaluation: `RLY-S21-SIDECAR-EVAL-006 — ESCALATE`
- Candidate: `ded3ed03b7070ea095a823129ebe44935cb57997`
- Requested provider/model: `openrouter / google/gemini-3.8-flash`

No new Human Authority and no Relay source change are introduced.

## Required corrections before V2 startup

Use the Human-selected ignored/untracked repository-root local credential file only. Verify it is present, ignored, untracked, and that tracked governance state is clean. Load the provider variable without emitting its value.

Create a fresh Run-007 disposable profile before any V2 process. At minimum create writable home, config, data, data/opencode, state, cache, tmp, and evidence directories. The parent directory of the configured `OPENCODE_DB` path must exist and be writable before the first V2 invocation.

Every V2 invocation, including version/help, explicit server startup, and utilities, must pass through one isolation wrapper. Direct V2 execution is forbidden. The wrapper may reference the local credential-file path but must never contain its secret value.

## Server startup

Prefer the same explicit loopback server command shape that succeeded in Run 004 if preserved sanitized evidence is available. Otherwise use only the installed beta's own wrapped help output to select its documented explicit headless server mode. Do not substitute TUI/background-daemon startup.

Use transient server connection authentication as in Run 004.

If the server exits before readiness, stop before candidate describe, provider discovery, or D21. Record the exit code and inspect only isolated Run-007 stdout/stderr and isolated V2 log/service/database path metadata. Retain only a sanitized diagnostic excerpt sufficient to classify the failure. Do not inspect protected V1 contents.

The failure report should distinguish only when evidence supports it: database/state path failure, service-registration failure, bind/listen failure, configuration parse failure, provider initialization failure, or runtime crash/other.

## Compatibility and D21 gates

Only after server readiness:
- authenticated `/api/health` must pass;
- unchanged candidate `OpenCodeRuntime.describe()` must pass;
- connection-auth leak check must pass;
- OpenRouter must be available from the existing provider credential;
- exact model `google/gemini-3.8-flash` must be available.

No alternate model.

Only after those gates pass may the remaining D21 protocol run with fresh Run-007 fixture/workspace/session/execution identities.

## Required report

Return authorities, handoff, governance head, candidate, credential-source gate result, disposable-directory/writability result, `OPENCODE_DB` parent result, wrapper-only invocation result, V1 integrity, V2 version/hash, server startup result and sanitized failure category if any, authenticated health, candidate describe, requested/actual provider-model identity, D21-01..18, credential leak check, candidate/source changes NONE, real-project calls NONE, evidence path, checksum, and deviations.

Do not issue ACCEPT, REWORK, Human technical acceptance, promotion, Slice closure, Slice 2.2 authority, or Phase 3 authority.
