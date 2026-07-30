# EVO — Evolutionary Virtual Organism

EVO Terrarium v0.1.1 is a bounded environment for experiments in evolutionary
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
- an offline test suite based entirely on the Python standard library.

It does **not** autonomously register accounts, accept legal terms, bypass
identity checks, obtain credentials, spend money, or deploy changes.

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

The result is written to `.evo/audit.jsonl`. A proposal is not applied to the
repository in v0.1; it is evaluated as data.

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
- search the redacted audit trail.

Use `--no-browser` if you prefer to open the page yourself, and `--port` to choose
a different local port.

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
