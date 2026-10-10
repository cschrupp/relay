# Slice 3.1 - Coding Agent Execution

**Status:** FUTURE SLICE PROPOSAL - NOT OPEN / NOT AUTHORIZED  
**Phase:** 3 - First Governed Autonomous Engineering Loop  
**Roadmap authority:** `RLY-P2-ROADMAP-REBASE-001 - AUTHORIZED`  
**Planned runtime:** `OpenCodeRuntime` through Relay `AgentRuntime`

## Objective

Execute one authorized implementation role in one authorized workspace through the Relay-owned AgentRuntime contract and return a normalized implementation result without allowing the implementation agent to accept or promote its own work.

## Upstream prerequisites

This future Slice may not open until the relevant upstream work is separately accepted or explicitly superseded:

```text
1.8 Governance Assurance Reference Model
1.9 Human Decision Support and Governance Review Surface
1.10 Canonical Source and Promotion Enforcement
2.2 Role Contracts
2.3 Context and Work-Packet Contract
2.4 Execution Workspace Authority
```

Phase 3 itself requires explicit Human opening authority.

## Planned execution path

```text
Relay authorization
      -> Role Contract
      -> Context / Work Packet
      -> Execution Workspace
      -> AgentRuntime
      -> OpenCodeRuntime
      -> configured provider/model
      -> normalized result + evidence
```

## Core invariants

- exact authorized baseline;
- exact Role Contract;
- deterministic Work Packet;
- explicitly authorized workspace;
- runtime permission cannot create Relay authority;
- resulting commit/evidence captured exactly;
- provider/model/runtime identity recorded;
- implementation cannot evaluate, accept, or promote itself;
- no automatic push/merge without separate authority.

## Hard stop

A successful coding-agent run is a submitted result, not an accepted or promoted result.
