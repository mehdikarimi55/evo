# EVO Terrarium Roadmap

## v0.1.1 — Execution and evaluation sandbox

Target loop:

`proposal → ephemeral worktree → validated patch → sandboxed tests → fitness
measurement → evidence archive → cleanup`

- [x] Rootless, fail-closed container sandbox runner
- [x] Credential-free environment, disabled network, resource ceilings
- [x] Explicit evaluator command allowlist
- [x] Ephemeral Git worktree manager
- [x] Structured patch validation and mutation applicator
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

## v0.2 — Autonomous lineage

- [x] Persistent bounded autonomous generation loop
- [x] Selected-adaptation memory
- [x] Evolution journal and milestone achievements
- [x] English/Persian observatory UI

## v0.3 — Digital Petri Dish

- [x] Persistent bounded founder population
- [x] Simulated energy costs and rewards
- [x] Multi-objective fitness and parent selection
- [x] Heredity with bounded deterministic trait mutation
- [x] Reproduction, carrying capacity, and extinction
- [x] Parent-child lineage evidence
- [x] Bilingual population observatory and lineage visualization
- [ ] Baseline/candidate execution fitness from the rootless sandbox
- [x] Deterministic replay package for complete ecological epochs

## v0.4 — Niches and primitive self-organization

Reliability gate: v0.3 population invariants, persistence, UI API, and the
complete offline suite passed before v0.4 began.

- [x] Environmental resource pools and changing selection pressures
- [x] Explicitly measurable ecological niches
- [x] Bounded organism-to-organism cooperation signals
- [x] Cooperation energy accounting and persistent interaction evidence
- [x] Emergent role detection based on observed behaviour
- [x] Diversity preservation and anti-monoculture selection
- [x] No new host capabilities or production-promotion authority
- [x] Multi-organism task decomposition with explicit bounded responsibilities
- [x] Quantitative open-endedness-proxy and ecological stability metrics

## v0.5 — Cooperative evidence

- [x] Complementary teams of at most three living organisms
- [x] Role-derived task decomposition with a single integration rule
- [x] Explicit proposal-only versus sandbox-verified evidence states
- [x] Hash-only persistent evaluator evidence from the rootless sandbox
- [x] Ecological stability and population-diversity metrics
- [x] Honest open-endedness proxy with bounded history
- [x] Candidate patch generation wired to the mutation/worktree pipeline
- [x] Automatic baseline-versus-candidate sandbox comparison
- [x] Deterministic replay package for complete ecological epochs

## v0.6 — Ephemeral candidate lifecycle

- [x] Second bounded model call for a raw unified diff
- [x] Maximum 32 KiB source context from one authorized target
- [x] Existing immutable patch policy reused without bypasses
- [x] Clean-repository baseline requirement
- [x] Ephemeral candidate branch/worktree with guaranteed cleanup
- [x] Identical rootless baseline and candidate evaluation commands
- [x] Regression, preserved-baseline, and repaired-baseline classification
- [x] Promotion eligibility requires verified comparative evidence
- [x] Bilingual sandbox configuration and lifecycle evidence UI
- [x] Deterministic replay package for complete ecological epochs
- [ ] Signed evidence bundles and external human promotion approval

## v0.7 — Deterministic evidence and human gate

- [x] Complete bounded replay inputs for ecological epochs
- [x] Fresh-state replay with deterministic organism-selection verification
- [x] Canonical timestamp-free state digest comparison
- [x] Host-authenticated HMAC-SHA256 evidence bundles
- [x] Mode-0600 local signing-key enforcement
- [x] Signed approve/reject records from an explicit local reviewer
- [x] Bilingual evidence and promotion-gate observatory
- [x] CLI and localhost API for bundle creation and review
- [x] No merge, push, deployment, or production authority
- [ ] External identity verification and independent production approval

## v0.8 — Public trust authority

- [x] Ed25519 authority identity with mode-0600 private-key enforcement
- [x] Publicly verifiable evidence attestations bound to bundle SHA-256
- [x] Independent reviewer key generation outside the repository
- [x] Explicit reviewer public-key registration and revocation
- [x] Ed25519-signed approve/reject records bound to one attestation
- [x] Fail-closed JSON policy requiring trusted independent approval
- [x] Signed manual-promotion authorization artifacts
- [x] Bilingual public-trust observatory and localhost API
- [x] No Git mutation, commit, merge, push, deployment, or production authority
- [ ] Independent production deployment controller and rollback authority

## v0.9 — Reproducible local promotion

- [x] Mode-0600 sealed patch retained only after sandbox verification
- [x] Ed25519 manifest binds patch, evidence, base commit, and mutable paths
- [x] Authorized bundle must cover the exact artifact manifest and patch hashes
- [x] Clean-repository and exact-tested-HEAD promotion preconditions
- [x] Explicit confirmation phrase before any local working-tree mutation
- [x] One-time consumption of independent promotion authorization
- [x] Signed local promotion ledger with post-state digest
- [x] Exact-state rollback before human edits or commits
- [x] Read-only bilingual release observatory; apply/rollback remain CLI-only
- [x] No staging, commit, merge, push, deployment, or production credentials
- [ ] External production deployment, health verification, and rollback service

## v1.0 — Signed external deployment handoff

- [x] Release capsule bound to one exact human commit and tested artifact
- [x] Ed25519-signed stage, health, production, and rollback intents
- [x] Independent operator identity creation, registration, and revocation
- [x] Offline operator receipt creation with deployment references
- [x] Fail-closed receipt import and one-receipt-per-intent enforcement
- [x] Latest-health gating before production promotion
- [x] Signed rollback request and independently observed rollback receipt
- [x] Read-only English/Persian deployment observatory
- [x] No cloud credentials, deployment API client, or network execution in EVO
- [ ] Provider-specific deployment adapter owned by a separate operator system

## Production gate

No candidate may reach production until deterministic replay, security
evaluation, rollback, signed artifacts, resource ceilings, and human approval
have all been implemented and independently tested.
