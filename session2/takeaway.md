### 1. Structure beats intelligence
- If the system is structured, dumb agents succeed.
- If it isn’t, smart agents still fail.

LLM quality matters less than:
- clear module boundaries
- a single source of truth 
- explicit invariants

You don’t “prompt” your way out of a messy repo.

### 2. Guardrails must be executable, not documented

If a rule isn’t enforced by code, it will be violated by an agent.
- AGENTS.md is useless unless tests fail

Policies must:
- live in code
- break CI
- produce proof artifacts

Queast treats “how work is done” as part of the system, not tribal knowledge.

This is where your proof CLIs, invariant tests, and “no hardcoded prompts” checks really land.

### 3. Trust comes from proof, not hope
You can refactor aggressively only if you can prove nothing broke.

- LLM-heavy systems drift by default
- The only antidote is:
- stable JSON outputs
- repeatable CLI proofs
- contracts & tests that survive refactors

Queast doesn’t ask you to believe the system—it gives you receipts.
