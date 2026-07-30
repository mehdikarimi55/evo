# EVO Terrarium Roadmap

## v0.1.1 — Execution and evaluation sandbox

Target loop:

`proposal → ephemeral worktree → validated patch → sandboxed tests → fitness
measurement → evidence archive → cleanup`

- [x] Rootless, fail-closed container sandbox runner
- [x] Credential-free environment, disabled network, resource ceilings
- [x] Explicit evaluator command allowlist
- [x] Ephemeral Git worktree manager
- [ ] Structured patch proposal and mutation applicator
- [ ] Baseline and candidate test/benchmark evaluator
- [ ] Reproducible candidate evidence package
- [ ] Candidate archive and lineage database

## v0.1 — Cell boundary

- [x] Immutable policy and budget kernel
- [x] Provider-neutral model interface
- [x] Groq and NVIDIA NIM capability adapters
- [x] Structured mutation proposal
- [x] Redacted append-only audit
- [x] Offline unit tests
- [x] Localhost web UI for configuration and one-generation runs

## v0.2 — Controlled reproduction

- Generate several bounded genome variants.
- Execute candidates in isolated worktrees and containers.
- Measure correctness, regression, runtime, token usage, and novelty.
- Preserve Pareto-front candidates rather than a single winner.
- Require signed kernel approval before archive admission.

## v0.3 — Memory organs

- Episodic execution records.
- Semantic lessons derived only from verified outcomes.
- Procedural recipes with provenance and expiry.
- Negative memory for failed approaches.
- Lineage memory for inherited mutations.

## v0.4 — Resource ecology

- Discover documented models, datasets, and free tiers.
- Produce provider proposals and adapters in a sandbox.
- Require owner approval for account creation, terms, identity, credentials,
  payment instruments, or spend.
- Introduce a simulated compute economy before any real financial budget.

## Production gate

No candidate may reach production until deterministic replay, security
evaluation, rollback, signed artifacts, resource ceilings, and human approval
have all been implemented and independently tested.
