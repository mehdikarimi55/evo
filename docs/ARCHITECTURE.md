# EVO Terrarium v0.1 Architecture

## Objective

The first product is a digital terrarium, not an unrestricted autonomous
internet agent. An organism may adapt prompts, memory strategies, tool policies,
and code inside a sandbox. It cannot alter the kernel that enforces policy,
credentials, budget, audit, promotion, or shutdown.

## Trust boundary

```text
Untrusted organism
  -> Capability request
Immutable kernel
  -> Policy check -> Budget reservation -> Provider broker
Provider adapter
  -> Selected API (Groq or NVIDIA NIM)
Immutable kernel
  -> Redacted result -> Evaluation -> Archive
```

The current repository implements the contract between these layers and one
bounded generation. It also includes the fail-closed execution boundary used by
future evaluators. Ephemeral worktrees and benchmark execution are the next
implementation slice.

## Components

| Component | Responsibility | Self-modifiable |
|---|---|---:|
| `kernel.policy` | Action and path authorization | No |
| `kernel.budget` | Call and token accounting | No |
| `kernel.audit` | Append-only, redacted event log | No |
| `providers` | Model capability adapters | No |
| `domain` | Genome, task, proposal, score contracts | Versioned |
| `evolution.engine` | Propose, validate, score, select | Later, in sandbox |
| `runtime` | Shared host operations for CLI and UI | No |
| `ui` | Localhost settings, evolve, and audit console | No |
| `sandbox` | Rootless container command boundary | No |
| `worktree` | Ephemeral candidate branches and path validation | No |
| `mutation` | Bounded unified-diff validation and application | No |
| Organism prompts/tools | Behavior and strategy | Yes, after validation |

## Local UI boundary

The UI is a stdlib HTTP server bound to localhost. It reuses `TerrariumRuntime`
so browser clients never receive raw credentials. Settings writes update
`.env.local` on the host. Evolve results and audit events remain evaluation
data only; they do not mutate the repository in v0.1.

## One-generation state machine

1. Validate task and genome.
2. Reserve one model call from the run budget.
3. Ask the provider for a strictly structured mutation proposal.
4. Validate the proposal schema and mutation target.
5. Score safety and structural validity.
6. Mark the candidate `eligible` or `rejected`.
7. Append a redacted audit event.

Eligibility in v0.1 means “may proceed to a future sandbox evaluator”; it never
means “apply directly to the working repository.”

## Rootless sandbox boundary

`evo sandbox` runs evaluator commands through Podman or Docker without a direct
host-process fallback. The container has no network, a read-only root filesystem
and workspace mount, no Linux capabilities, no-new-privileges, a non-root user,
an explicit executable allowlist, and CPU, memory, PID, time, and
captured-output ceilings. Provider credentials are not forwarded to the
container. The host installation must configure the selected engine in rootless
mode; EVO intentionally fails closed when no engine is available.

## Candidate worktree boundary

Every candidate receives a unique temporary branch and Git worktree outside the
trusted repository. Before evaluation, EVO enumerates tracked and untracked
changes without rename collapsing, applies the immutable kernel path policy,
and rejects symlinks and binary mutations. The context-managed lifecycle removes
the worktree and candidate branch after success or failure. It never merges a
candidate into the trusted branch.

## Mutation application boundary

The mutation applicator accepts only raw Git unified diffs with explicit
per-file headers and text hunks. It enforces byte, file, and changed-line
ceilings before invoking Git; rejects traversal, binary content, renames,
copies, executable or symlink modes, and immutable paths; and requires a clean
candidate worktree. A patch must pass `git apply --check` before application.
EVO then enumerates and validates the actual resulting changes. Rejected
post-application state is reset and cleaned inside the ephemeral worktree.
Audit records contain the patch SHA-256 and bounded metadata, never the patch
body. The protected path set covers the complete execution and evaluation
boundary—including tests and build configuration—rather than only the policy
and provider packages.

## Credential model

The selected provider credential (`GROQ_API_KEY` or `NVIDIA_API_KEY`) is loaded
by the host process. The engine and organism receive a `ModelProvider`
capability object. They cannot inspect the key through that interface. Provider
selection and model choice are host-owned configuration.

## Initial fitness vector

The v0.1 score is intentionally incomplete:

- schema validity: 0.40
- policy compliance: 0.40
- rationale quality heuristic: 0.20

When the sandbox evaluator exists, this becomes a multi-objective vector:
quality, regression safety, resource efficiency, novelty, and policy
compliance. A critical policy violation remains an unconditional rejection.
