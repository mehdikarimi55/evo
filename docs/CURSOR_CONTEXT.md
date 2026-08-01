# EVO Terrarium — Cursor Development Context

Read this file before changing the project. It is a technical handoff for an AI
coding assistant continuing EVO in Cursor. The authoritative detailed documents
are `README.md`, `docs/ARCHITECTURE.md`, `docs/OPERATIONS.md`, and
`docs/ROADMAP.md`; update them whenever behavior or boundaries change.

`docs/PRODUCT_BRAIN_BLUEPRINT.md` is a design-only greenfield blueprint for a
sibling Product Brain project (idea → lifelong products). Do not implement it
inside EVO Terrarium unless the user explicitly requests a fork/rebrand; keep
terrarium safety invariants intact.

## Current repository state

- Product: EVO — Evolutionary Virtual Organism / Digital Petri Dish
- Current version: `1.1.0`
- Python: 3.12+
- Package: `evo-terrarium`
- CLI entry point: `evo = evo.cli:main`
- Current development branch at handoff:
  `codex/evo-v1.1-evolution-operations`
- v1.1 is implemented locally but may still be uncommitted. Inspect
  `git status --short --branch` before editing.
- The last verified suite result was 128 tests passing.
- Untracked `.DS_Store` and `deliverables/` existed before this handoff. They
  are user-owned and must not be deleted, staged, or modified unless explicitly
  requested.

## Product vision

EVO is a bounded research environment for digital abiogenesis, artificial life,
and open-ended evolutionary coding experiments. It models a population of
digital organisms with simulated energy, heredity, reproduction, selection,
ecological niches, cooperation, emergent roles, and lineage. Organisms can ask
an external model provider to propose adaptations, and the host can evaluate a
candidate inside a locked-down rootless container.

The goal is not to build an unrestricted self-deploying agent. The goal is to
study increasingly autonomous evolutionary behavior while retaining a hard,
human-owned safety boundary around credentials, budgets, execution, source-code
promotion, and deployment.

## Non-negotiable safety invariants

Preserve these invariants in every change:

1. Organisms never receive raw provider keys or production credentials.
2. Provider keys are read from environment files and never returned by the API,
   UI, audit log, journal, evidence, or exception text.
3. The immutable kernel owns policy, budgets, audit, and authorization.
4. Model output is untrusted input. Validate schemas, paths, sizes, file types,
   and patch structure before use.
5. Candidate execution is fail-closed and rootless, with no network, a
   credential-free environment, read-only source mount, dropped capabilities,
   and resource limits. Never silently fall back to host execution.
6. Mutation is limited to declared mutable paths. Kernel, provider, operations,
   trust, release, deployment, and credential code remain protected.
7. `eligible` and `promotion_eligible` do not mean applied, committed, pushed,
   merged, or deployed.
8. Autonomous evolution must never stage, commit, push, promote, deploy, create
   accounts, accept terms, spend money, or bypass identity checks.
9. Local promotion requires the existing explicit human gate and exact
   confirmation. Deployment is performed only by a separate external operator.
10. State restoration must be explicit, confirmed, and performed while
    autonomous evolution is stopped.
11. Security and evidence records should remain bounded, redacted, and
    tamper-evident. Do not store raw patches or test output where only digests
    are intended.
12. Simulated energy is an ecological variable, not currency or provider quota.

If a requested feature conflicts with these rules, keep the safe boundary and
explain the conflict rather than weakening enforcement.

## Implemented evolution path

- v0.1: provider-neutral model interface, immutable kernel, budget, policy,
  structured proposals, audit, and localhost UI.
- v0.2: bounded autonomous loop, persistent journal, and achievements.
- v0.3: Digital Petri Dish population, energy, heredity, reproduction,
  selection, extinction, and lineage.
- v0.4: resource cycles, niches, cooperation, emergent roles, and diversity
  preservation.
- v0.5: bounded three-organism teams, role-derived decomposition, evaluator
  evidence, and ecological/open-endedness proxy metrics.
- v0.6: model-generated unified diffs, ephemeral worktrees, identical baseline
  and candidate sandbox evaluation, and comparative evidence.
- v0.7: deterministic ecological replay, HMAC evidence bundles, and a local
  human review gate.
- v0.8: Ed25519 public attestations, independent reviewer identities,
  revocation, immutable policy, and signed manual-promotion authorization.
- v0.9: sealed candidate artifacts, one-time confirmed local promotion, and
  deterministic rollback.
- v1.0: signed external deployment handoff intents and independently signed
  operator receipts. EVO itself has no cloud deployment authority.
- v1.1: persistent evolution operations, readiness preflight, headless running,
  schedules, daily budgets, circuit breaking, checkpoints, alerts, metrics,
  and a controlled candidate review queue.

## v1.1 operational behavior

`src/evo/operations.py` is the v1.1 control plane. It wraps the autonomous
worker; it does not enter the organism or kernel trust domains.

Before each autonomous generation it checks:

- configured UTC operating window;
- persistent circuit-breaker state;
- daily attempt, provider-call, input-token, and output-token ceilings;
- living-population and mean-energy floors; and
- a conservative, persisted worst-case usage reservation.

Schedule or daily-budget exhaustion defers safely without consuming another
attempt. Repeated failures or unhealthy population state opens the persistent
circuit, disables the loop, records an alert, and requires the exact human
acknowledgement `RESUME-EVOLUTION`.

Readiness has two distinct signals:

- `ready_to_evolve`: provider configured and freshly probed, population alive,
  persistent directories usable, and circuit closed.
- `verified_code_evolution_ready`: all of the above plus a configured rootless
  sandbox. Without this, research continues only in proposal mode.

Provider probe success is persisted in `.evo/provider-health.json` with mode
0600. Operational state is stored under `.evo/operations/`. The worker records
restart/heartbeat evidence, bounded long-term metrics, local alerts, retained
checkpoints, and sandbox-verified candidate review entries. Queue decisions do
not promote or deploy anything.

Only one active evolution host should run at a time: either the web UI process
or `evo operations run`, not both.

## Architecture and important files

### Core boundaries

- `src/evo/kernel/policy.py`: action and mutable-path authorization.
- `src/evo/kernel/budget.py`: generation-scoped call/token accounting.
- `src/evo/kernel/audit.py`: append-only redacted security audit.
- `src/evo/domain.py`: shared data contracts.
- `src/evo/evolution/engine.py`: one bounded propose/validate/score/select loop.
- `src/evo/providers/`: Groq and NVIDIA NIM adapters behind one contract.
  NVIDIA decoding uses host-owned generation profiles (`precise`, `balanced`,
  `exploratory`) with JSON extraction and optional reasoning controls.

### Population and autonomy

- `src/evo/petri.py`: persistent population, ecology, fitness, reproduction,
  selection, cooperation, roles, lineage, metrics, and deterministic replay
  inputs.
- `src/evo/autonomy.py`: persistent worker lifecycle and journal integration.
- `src/evo/achievements.py`: host-owned milestone catalog and unlock rules
  (single source of truth for IDs, thresholds, and symbols).
- `src/evo/journal_story.py`: bilingual storytelling chronicle from journal
  entries for the Evolution Journey modal.
- `src/evo/content_i18n.py`: cached provider-backed Persian translation for
  Latin proposal free-text shown in journey/journal FA views.
- `src/evo/operations.py`: v1.1 scheduling, budgets, circuit, checkpoints,
  alerts, metrics, readiness, and review queue.
- `src/evo/runtime.py`: shared host facade used by CLI and UI. Provider health
  and operation usage are integrated here.

### Candidate and trust pipeline

- `src/evo/mutation.py`: bounded unified-diff validation and application.
- `src/evo/worktree.py`: ephemeral Git candidate branches/worktrees.
- `src/evo/sandbox.py`: rootless container execution boundary.
- `src/evo/evaluation.py`: hash-only evaluator evidence.
- `src/evo/candidate_lifecycle.py`: baseline/candidate comparison and sealed
  candidate production.
- `src/evo/evidence_control.py`: deterministic replay bundles and human gate.
- `src/evo/trust_authority.py`: Ed25519 attestations, reviewers, policy, and
  promotion authorization.
- `src/evo/release_control.py`: sealed local promotion and rollback.
- `src/evo/deployment_control.py`: signed external deployment handoff protocol.

### Interfaces

- `src/evo/cli.py`: all CLI commands, including `operations` actions.
- `src/evo/ui/server.py`: localhost standard-library HTTP API/server.
- `src/evo/ui/static/index.html`: bilingual application markup.
- `src/evo/ui/static/app.js`: API calls, English/Persian translations, rendering,
  hover-help tooltips for panels/cards, and observatory interactions.
  operations controls, charts, and state management.
- `src/evo/ui/static/app.css`: responsive visual system and RTL-aware layout.

## Persistent local state

Runtime state is intentionally outside source control under `.evo/`, including:

- `audit.jsonl`: redacted low-level audit trail;
- `autonomy-state.json`: persistent autonomous worker configuration/state;
- `evolution-journal.jsonl`: public progress narrative and achievements;
- `petri-dish.json`: population/ecology state;
- `provider-health.json`: most recent successful provider probe;
- `operations/state.json`: operations configuration, usage, circuit, heartbeat;
- `operations/checkpoints/`: retained autonomy and Petri Dish snapshots;
- evidence, trust, promotion, release, and deployment ledgers/artifacts.

Use atomic writes and restrictive mode 0600 for sensitive or authoritative
state. Do not commit `.env.local`, `.evo/`, private keys, patches, credentials,
or generated runtime state.

## Development and verification commands

From the repository root:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests -v
node --check src/evo/ui/static/app.js
.venv/bin/python -m compileall -q src tests
git diff --check
git status --short --branch
```

Tests are offline. UI tests bind an ephemeral localhost port, so an IDE sandbox
may need explicit loopback permission. Do not treat a socket `PermissionError`
as an application regression; rerun with permission and verify the final suite.

Every behavioral change should include focused tests in the matching
`tests/test_*.py` file. Changes crossing boundaries should also update runtime,
CLI, API, bilingual UI, documentation, and integration tests as applicable.

## Running EVO

```bash
cp .env.example .env.local
# Add EVO_PROVIDER and the selected provider's newly generated API key.

.venv/bin/evo doctor --env-file .env.local
.venv/bin/evo probe --env-file .env.local
.venv/bin/evo operations status --env-file .env.local
```

Interactive localhost UI:

```bash
.venv/bin/evo ui --env-file .env.local
# Open http://127.0.0.1:8787/
```

Headless operation:

```bash
.venv/bin/evo operations run --start --env-file .env.local
```

One bounded generation:

```bash
.venv/bin/evo evolve \
  --env-file .env.local \
  --task "Improve input validation without changing public behavior."
```

See `docs/OPERATIONS.md` for scheduling, checkpoints, circuit recovery,
macOS launchd, and Linux systemd examples.

## UI and API expectations

- English is the default language; Persian must be fluent and fully RTL.
- All newly visible text must be added in both languages in `app.js`.
- Keep typography compact, modern, readable, and related to the digital-life
  observatory concept.
- Long CLI/audit/result text must wrap and must not create horizontal page
  scrolling.
- Evolution activity must show a thinking/heartbeat state.
- Preserve responsive behavior at desktop and approximately 390 px mobile.
- The lineage map must render every generation (no truncated organism window)
  and remain navigable via scrollbars, zoom controls/wheel, and hand-drag pan.
- Never expose raw secrets in JSON responses or DOM state.
- Operationally dangerous actions belong in CLI-only workflows unless an
  existing architecture document explicitly permits otherwise.
- Main workspace panels and Petri ecology/lineage subsections are collapsible
  (`details`) and must start collapsed by default.
- Groq and NVIDIA model fields use a dropdown catalog (`/api/models`), merged
  with live provider listings when credentials are available.

When UI files change, verify English desktop, Persian RTL, mobile layout, no
horizontal overflow, no browser console errors, and all affected API actions.

## Coding conventions

- Prefer Python standard-library components unless a dependency is necessary;
  the intentionally pinned runtime dependency is `cryptography>=44,<50`.
- Use typed dataclasses and explicit exceptions for domain/control errors.
- Persist JSON deterministically where hashes/signatures depend on it.
- Bound all untrusted strings, arrays, histories, files, patches, and outputs.
- Fail closed on malformed state, signature mismatch, path ambiguity, sandbox
  absence, stale evidence, or authorization mismatch.
- Use locks for concurrent state updates. Never let UI and worker race on a
  ledger or state file.
- Keep timestamps UTC and explicit.
- Maintain deterministic behavior where replay depends on selection/outcomes.
- Preserve backward compatibility for existing state when adding fields by
  supplying safe defaults and validating migrations.
- Do not weaken a test merely to make it pass; fix the boundary or update the
  test only when intended behavior has genuinely changed.

## Recommended next phase

Treat v1.1 as an operational reliability gate before expanding evolutionary
complexity. First run a supervised soak test with a real provider and rootless
sandbox, using conservative daily limits. Confirm restart recovery, scheduled
deferral, quota accounting, circuit opening/resumption, checkpoint restoration,
metric continuity, and candidate queue behavior over multiple days.

A logical v1.2 should focus on **scientific experiment orchestration and
reproducibility**, not additional authority. Candidate objectives:

1. Declarative experiment manifests binding objective, seed, provider/model,
   ecology parameters, budgets, evaluator, and immutable code revision.
2. Replicated control/treatment runs with deterministic seeds and comparable
   stopping criteria.
3. Bounded experiment datasets and exportable provenance manifests without
   secrets, raw private patches, or deployment authority.
4. Statistical comparison of lineage survival, fitness, diversity, cooperation,
   ecological stability, and the open-endedness proxy.
5. Explicit anomaly detection for metric collapse, monoculture, runaway cost,
   repeated candidate duplication, and stalled novelty.
6. A bilingual experiment observatory showing hypotheses, runs, confidence,
   caveats, and reproducible evidence.

Do not claim genuine open-ended evolution, consciousness, life, or scientific
proof from proxy metrics. Label simulations and operational signals honestly.

## Workflow for the next AI developer

1. Read this file plus `README.md`, `docs/ARCHITECTURE.md`,
   `docs/OPERATIONS.md`, and `docs/ROADMAP.md`.
2. Inspect `git status`, the current branch, and the full diff before editing.
3. Preserve unrelated and user-owned changes.
4. Identify the precise trust boundary affected by the requested work.
5. Add tests first or alongside the implementation.
6. Integrate all applicable surfaces: runtime, CLI, API, English/Persian UI,
   documentation, and state compatibility.
7. Run the full offline test and syntax/hygiene checks above.
8. Never commit or push unless the user explicitly requests it.

