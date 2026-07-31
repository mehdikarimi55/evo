# EVO — Evolutionary Virtual Organism

EVO Terrarium v0.7.0 is a bounded environment for experiments in evolutionary
coding agents. It lets an organism propose a mutation, evaluates that mutation,
and records whether it is eligible for selection. The immutable kernel owns
credentials, budgets, policy decisions, audit events, and promotion gates.

This repository starts with a deliberately narrow vertical slice:

- a provider-neutral model contract;
- Groq and NVIDIA NIM adapters that read credentials only from the environment;
- an immutable policy boundary;
- a deterministic one-generation evolution engine;
- explicit token and call budgets;
- local JSONL audit records;
- a fail-closed rootless container command runner;
- a localhost web UI for settings, probe, evolve, and audit search;
- an English-first bilingual interface with persistent English/Persian switching;
- a bounded autonomous generation loop and public-facing evolution journal;
- persistent milestone achievements recorded against the evolving lineage;
- a persistent Digital Petri Dish population with bounded energy and capacity;
- heredity, reproduction, selection, extinction evidence, and lineage mapping;
- multi-objective fitness for validity, safety, reasoning, novelty, and efficiency;
- cycling environmental resources and measurable ecological pressures;
- bounded cooperation signals and behaviour-derived emergent roles;
- diversity-aware selection that resists premature niche monoculture;
- bounded three-organism teams with role-derived task decomposition;
- tamper-evident rootless sandbox evaluation records;
- ecological stability, population diversity, and open-endedness proxy metrics;
- bounded model-generated unified diffs using limited source context;
- ephemeral candidate worktrees and automatic baseline comparisons;
- deterministic replay of complete ecological epochs;
- host-authenticated evidence bundles and signed local review records;
- an explicit human-controlled promotion gate with no deployment authority;
- an offline test suite based entirely on the Python standard library.

It does **not** autonomously register accounts, accept legal terms, bypass
identity checks, obtain credentials, merge code, spend money, or deploy changes.

## Quick start

Python 3.12 or newer is required. Create an isolated environment and install
the project before running its commands:

```bash
python3.13 -m venv .venv
.venv/bin/python -m pip install -e .
.venv/bin/python -m unittest discover -s tests -v
```

The test suite is fully offline and does not require provider credentials.

To use a model provider, create a local environment file and add a newly
generated key for the selected provider:

```bash
cp .env.example .env.local
# Select EVO_PROVIDER and add a newly generated provider key to .env.local.
.venv/bin/evo doctor --env-file .env.local
.venv/bin/evo probe --env-file .env.local
```

The `probe` command makes one small request to the selected provider. The key
is never printed.

For NVIDIA NIM, configure:

```dotenv
EVO_PROVIDER=nvidia
NVIDIA_API_KEY=your-new-key
EVO_NVIDIA_MODEL=meta/llama-3.1-70b-instruct
```

For Groq, use `EVO_PROVIDER=groq`, `GROQ_API_KEY`, and `EVO_GROQ_MODEL`.

To run a single, bounded generation:

```bash
.venv/bin/evo evolve \
  --env-file .env.local \
  --task "Improve input validation without changing public behavior."
```

The result is written to `.evo/audit.jsonl`. Without a configured rootless
sandbox, the result remains a proposal and is never applied to the repository.

## Rootless sandbox

Evaluator commands can be run with a rootless Podman or Docker installation:

```bash
.venv/bin/evo sandbox \
  --image python:3.13-alpine \
  --workspace . \
  -- python -m unittest discover -s tests -v
```

The sandbox has no network and mounts the workspace read-only. It drops
capabilities, runs as a non-root user, strips provider credentials, and applies
time, memory, CPU, PID, and output limits. Only `python`, `python3`, and `pytest`
are permitted by default; use a repeated `--allow-command NAME` option to
provide a narrower or project-specific allowlist. EVO does not fall back to
executing the command directly on the host.

## Ephemeral candidate worktrees

The v0.1.1 evaluation boundary creates each candidate on a unique temporary Git
branch and worktree. Changes are accepted for evaluation only when every path
is inside the genome's mutable paths and no mutation targets the immutable
kernel, creates a symlink, or introduces a binary file. Worktrees and candidate
branches are removed after evaluation, including when evaluation raises an
error. Candidates are never merged automatically.

## Structured mutation patches

EVO v0.1.1 can validate and apply a model-produced unified diff inside an
ephemeral candidate worktree. The applicator limits patch bytes, file count, and
changed lines; rejects protected paths, traversal, binary patches, symlinks,
renames, copies, and executable modes; and verifies the patch with
`git apply --check`. After application, the resulting worktree paths are checked
again. Audit evidence stores only the patch SHA-256 and bounded metadata, not
the source patch.

## Local UI

Start the localhost UI (binds only to `127.0.0.1` by default):

```bash
.venv/bin/evo ui --env-file .env.local
```

Open [http://127.0.0.1:8787/](http://127.0.0.1:8787/). From the UI you can:

- save provider settings into `.env.local` without displaying raw keys;
- run doctor and probe checks;
- run one bounded generation;
- switch between English (default) and Persian;
- start or stop bounded autonomous evolution;
- follow the gnome's progress in a dedicated evolution journal;
- search the redacted audit trail.

Use `--no-browser` if you prefer to open the page yourself, and `--port` to choose
a different local port.

## Autonomous evolution

Autonomous mode repeatedly asks the configured model provider for one bounded
mutation proposal on behalf of a selected population member, evaluates it
against the immutable policy, updates that organism's energy and fitness, and
records the result. Eligible organisms may reproduce after accumulating enough
energy; offspring inherit bounded adaptations and mutated traits. Its default
objective explores digital abiogenesis and artificial life through open-ended,
self-organizing multi-agent systems.

To use it:

1. Configure and probe a provider in the local UI.
2. Review the objective, mutable paths, interval, and attempt limit.
3. Select **Start autonomous evolution** once.
4. Keep the EVO UI process running. If the provider or internet connection is
   temporarily unavailable, the worker records the failure and retries after
   the configured interval.

The enabled state is persisted in `.evo/autonomy-state.json`, so autonomous mode
resumes when the UI process is started again. The public progress narrative is
stored in `.evo/evolution-journal.jsonl`; the lower-level security audit remains
in `.evo/audit.jsonl`.

Selected generations also unlock persistent lineage achievements. Milestones
currently mark the first viable adaptation and generations 5, 10, 25, 50, 100,
500, and 1,000. Every unlock is attached to the exact journal entry that earned
it and appears in the Evolutionary Achievements gallery.

Autonomous mode is deliberately opt-in because each generation consumes API
quota. It has a configurable attempt limit (maximum 10,000), a minimum
30-second interval, and never applies or promotes source changes. Applying
tested mutations inside candidate worktrees can be added as a later promotion
stage with a separate approval policy.

## Digital Petri Dish

The Petri Dish starts with six founder organisms and a carrying capacity of 24.
Each autonomous attempt selects one living organism using measured fitness,
available energy, and evaluation history. Evaluation consumes energy. Eligible,
safe, novel adaptations restore energy and can trigger reproduction; rejected
proposals reduce viability. When capacity is exceeded, the least viable
organisms become extinct.

Population state is stored atomically in `.evo/petri-dish.json`. The UI exposes
energy, fitness, births, extinctions, founder/offspring status, and a scrollable
parent-child lineage graph. This simulated substrate grants no additional host
permissions and cannot promote its own mutations.

## Niches and primitive self-organization

The v0.4 ecology cycles deterministically through balanced, scarcity,
novelty-surge, and stability phases. Compute, knowledge, novelty, and stability
resources replenish and are consumed independently. Organism fitness therefore
depends partly on how inherited traits fit the current environment.

Before each generation, EVO may expose one bounded cooperation context from a
complementary living organism. It contains only a public organism identifier,
an observed role, and the latest verified adaptation summary. Successful
cooperation rewards both participants with simulated energy and records a
bounded interaction edge. It does not share credentials, tools, processes, or
write access.

Explorer, guardian, economizer, archivist, and generalist roles are inferred
from observed fitness and inherited traits; they are not assigned as executable
agent privileges. Carrying-capacity selection gives rare observed roles a
preservation advantage to reduce premature monoculture.

## Cooperative evidence and research metrics

In v0.5, EVO forms a deterministic team of at most three complementary living
organisms. The lead integrates bounded advice from role-derived
responsibilities. These responsibilities are prompt context only: they do not
grant tools, credentials, network access, or permission to promote code.

Ordinary model output remains labelled `proposal_only`. When an executable
candidate artifact exists, the host can run an explicit evaluator and record
hash-only evidence:

```bash
.venv/bin/evo evaluate \
  --workspace . \
  --image python:3.13-alpine \
  --candidate-id candidate-0001 \
  --team-id gnome-0001 \
  --team-id gnome-0002 \
  -- python -m unittest
```

The ledger stores command, outcome, duration, output hashes, timeout, and
truncation state in `.evo/evaluation-evidence.jsonl`; it does not persist raw
test output. The Petri Dish also reports ecological stability, population
diversity, and an open-endedness proxy based on novelty, adaptation diversity,
and lineage branching. This is an operational signal, not proof of truly
unbounded evolution.

## Ephemeral candidate lifecycle

v0.6 can turn an eligible proposal into a bounded unified diff. The model sees
at most 32 KiB from one policy-authorized target file. EVO validates the diff,
creates a temporary Git branch and worktree outside the trusted repository,
runs the configured evaluator against both the clean baseline and candidate,
records hash-only comparison evidence, and destroys the temporary branch.

Enable the lifecycle in `.env.local` or the bilingual Settings panel:

```dotenv
EVO_SANDBOX_IMAGE=python:3.13-alpine
EVO_SANDBOX_ENGINE=podman
EVO_EVALUATION_COMMAND=python -m unittest discover -s tests
EVO_SANDBOX_TIMEOUT_SECONDS=60
```

The engine must be rootless. Containers receive no network, credentials, host
write access, elevated capabilities, or promotion authority. A dirty repository
fails closed because baseline and candidate evidence would not be comparable.
Passing evidence sets `promotion_eligible` only; it does not merge, commit,
push, deploy, or modify the original worktree.

## Deterministic replay and human promotion gate

v0.7 records the bounded candidate input required to replay every ecological
epoch. Before an evidence bundle is created, EVO reconstructs a fresh Petri
Dish, repeats deterministic organism selection and every recorded outcome, and
compares a canonical timestamp-free SHA-256 state digest. The complete replay
history is bounded to 10,000 epochs.

Evidence bundles include the replay manifest and candidate-evaluation ledger.
They are authenticated with HMAC-SHA256 using a 32-byte, mode-0600 host key at
`.evo/evidence-signing.key`. This proves integrity to the same host; it is not a
publicly verifiable identity signature. Use the UI promotion gate or CLI:

```bash
.venv/bin/evo evidence bundle
.venv/bin/evo evidence approve --approver "Local reviewer" \
  --note "Replay and sandbox evidence inspected."
.venv/bin/evo evidence status
```

An approval is a signed local human assertion. It never merges, pushes, or
deploys, and `deployment_authorized` remains false. Production promotion still
requires an independently authenticated external approval and deployment
system.

## Security invariants

1. Organisms receive capabilities, never raw credentials.
2. External side effects are denied unless an immutable policy explicitly
   allows them.
3. Mutation targets must stay within configured mutable paths.
4. Every model call consumes a bounded call/token budget.
5. A mutation cannot promote itself.
6. Audit records redact common API-key formats.
7. Production deployment and financial actions always require an external
   approval system.

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) and
[docs/ROADMAP.md](docs/ROADMAP.md) for the system boundary and next milestones.
