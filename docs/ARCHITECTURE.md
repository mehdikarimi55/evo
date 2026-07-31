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

## Digital Petri Dish population boundary

The v0.3 population substrate wraps the existing bounded generation engine; it
does not enter or replace the immutable kernel. Before an autonomous attempt,
the Petri Dish selects a living organism using fitness, energy, and evaluation
diversity. The organism contributes only public traits and inherited adaptation
summaries to the generation request.

After the kernel returns an eligible or rejected candidate, the Petri Dish:

1. charges a fixed simulated evaluation cost;
2. derives a bounded fitness vector from validity, policy safety, rationale,
   novelty, and simulated efficiency;
3. rewards eligible adaptations or penalizes rejection;
4. reproduces sufficiently energetic organisms;
5. passes bounded adaptation memory and mutated scalar traits to offspring;
6. enforces carrying capacity through viability-based selection; and
7. atomically records population, birth, extinction, and lineage evidence.

Population energy is a simulation variable, not money or provider quota.
Reproduction does not copy credentials, create processes, apply patches, or
grant capabilities. The Petri Dish state is host-owned
`.evo/petri-dish.json`; organisms cannot write it directly.

## v0.4 ecology and cooperation boundary

The host-owned environment has four simulated resource pools—compute,
knowledge, novelty, and stability—and four deterministic phases: balanced,
scarcity, novelty surge, and stability. These values influence simulated
fitness and energy rewards only. They cannot alter provider budgets or host
resource limits.

Before a bounded generation, the population layer may select one complementary
living organism. The request receives a cooperation context containing only
its public identifier, observed role, and latest verified adaptation summary.
No organism-to-organism channel can transfer secrets, invoke tools, or write
state. After evaluation, cooperation results are recorded as bounded counters
and simulated energy effects.

Roles are derived from observed validity, safety, reasoning, novelty,
efficiency, environmental fit, cooperation, and inherited traits. They are
descriptive evidence—not permissions or fixed agent assignments. Capacity
selection includes a rare-role preservation term so ecological diversity is
less likely to collapse into a monoculture.

## v0.5 cooperative evidence boundary

The population layer deterministically selects a lead and up to two
complementary collaborators. A team plan gives each organism one descriptive
responsibility and a single integration rule. Team size is capped at three and
the plan cannot create processes, communicate outside the request, or override
kernel policy.

Provider proposals are labelled `proposal_only` unless the host supplies
concrete evaluation evidence. `evo evaluate` executes an allowlisted command
through the existing rootless sandbox and appends command metadata, outcome,
duration, and SHA-256 output digests to a host-owned JSONL ledger. Failed tests
are retained as evidence but are never labelled verified. Raw evaluator output
is intentionally excluded from the ledger.

Ecological stability combines population survival, energy/fitness variation,
and resource balance. Population diversity combines normalized role entropy
and inherited trait dispersion. The open-endedness proxy combines recent
novelty, unique adaptation rate, and lineage branching. All values are bounded
between zero and one and retain a 500-epoch history. They are observability
signals, not a scientific demonstration of unlimited open-ended evolution.

## v0.6 ephemeral candidate lifecycle

After policy accepts proposal metadata, a second budgeted provider request may
generate one raw unified diff. The provider receives at most 32 KiB from the
authorized target file. Protected paths, binary content, symlinks, oversized
files, traversal, and multi-target policy violations fail before evaluation.

The host requires a clean repository, evaluates the baseline in a read-only
rootless sandbox, applies the diff through `MutationApplicator` inside an
ephemeral `GitWorktreeManager` candidate, and evaluates the candidate with the
same command and limits. Cleanup removes both temporary worktree and branch,
including after rejection or evaluator failure.

The candidate evidence ledger contains patch/output hashes, changed paths,
exit codes, duration, team identifiers, and comparison classification. It does
not contain raw source, patches, test output, credentials, or environment
secrets. `promotion_eligible` means only that comparative evaluation passed; no
component in this lifecycle can modify the source worktree or promote a change.

## v0.7 deterministic evidence and approval boundary

Each ecological event stores a bounded replay input without source patches or
credentials. Bundle creation reconstructs a new Petri Dish from its founder
parameters, verifies that deterministic selection chooses the recorded
organism at every epoch, applies the recorded outcome, and compares a canonical
timestamp-free SHA-256 digest. Missing or divergent history fails closed.

The evidence bundle covers the replay manifest and candidate-evidence ledger.
HMAC-SHA256 authenticates it with a host-owned 32-byte key whose filesystem
mode must be 0600. Because this is symmetric authentication, it establishes
integrity for the same host—not public authorship or reviewer identity.

The human gate accepts only a verified latest bundle and records an explicit
approve or reject assertion with reviewer label, note, timestamp, and HMAC. It
does not authenticate a person, modify Git, or authorize deployment. The API
does not accept arbitrary bundle paths, and all responses report deployment
authorization as false.

## v0.8 public trust and policy boundary

The v0.8 trust authority wraps the latest verified v0.7 bundle in an Ed25519
attestation bound to the exact bundle SHA-256. The authority key is a raw
32-byte mode-0600 private key. Its public key and SHA-256 fingerprint can be
distributed for verification without sharing signing authority.

Independent reviewers use separate Ed25519 identities created at explicit
paths outside the repository. EVO registers only their public keys. A review is
bound to one attestation ID, bundle ID, bundle digest, decision, reviewer
fingerprint, note, and timestamp. A revoked identity immediately stops
qualifying for policy evaluation, including reviews signed before revocation.

The host-owned JSON policy requires a valid public attestation, rejects revoked
reviewers, and requires one to five distinct trusted approvals. Immutable
fields prevent the policy from granting deployment or widening its scope beyond
manual repository promotion. A passing policy can produce an Ed25519-signed
authorization artifact, but the trust authority has no Git mutation, commit,
merge, push, deployment, credential, or rollback capability. This keeps trust
decisions outside the evolving population and execution remains a separate
human-owned concern.

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
