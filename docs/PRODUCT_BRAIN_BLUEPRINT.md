# Product Brain — Greenfield Blueprint

**Status:** design only (not implemented in EVO Terrarium)  
**Purpose:** architecture and phased roadmap for a **new project from scratch**  
**Scope:** domain-agnostic — any idea becomes a product; products improve for life

This document is independent of EVO Terrarium’s Petri Dish mission. EVO can
inspire patterns (immutable kernel, budgets, sandbox, audit), but Product Brain
is a separate product whose primary object is a **living product**, not an
organism in a dish.

---

## 1. Vision

> An intelligent host brain that converts **any idea** into a **working product**,
> then continuously **mutates, tests, improves, and monitors** that product for
> its lifetime — while an immutable core keeps secrets, budgets, and safety gates
> out of the product’s reach.

Non-goals for the core platform:

- Hardcoding any domain (finance, news, games, etc.)
- Guaranteeing business outcomes
- Autonomous cloud deploy, payments, or account creation
- Letting products rewrite the brain’s policy or credentials

---

## 2. Clean architecture

### 2.1 Layer diagram

```text
┌─────────────────────────────────────────────────────────────────┐
│  Interfaces                                                     │
│  CLI · Local UI · API (localhost) · Event / webhook adapters    │
└────────────────────────────▲────────────────────────────────────┘
                             │ commands / queries
┌────────────────────────────┴────────────────────────────────────┐
│  Application (use cases)                                        │
│  SubmitIdea · AdvanceStage · ProduceVersion · VerifyVersion     │
│  ActivateProduct · ObserveHealth · ProposeMutation · Select     │
│  ScheduleWork · PauseMission · ResumeMission                    │
└────────────────────────────▲────────────────────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│  Domain                                                         │
│  Idea · ProductSpec · Blueprint · ProductVersion · Evidence     │
│  Mission · Stage · Fitness · Observation · ImprovementBacklog   │
│  PolicyDecision · BudgetLedger · ToolCapability                 │
└────────────────────────────▲────────────────────────────────────┘
                             │ ports
┌───────────────┬────────────┴────────────┬───────────────────────┐
│ Brain Kernel  │ Factory Runtime         │ Product Workspaces    │
│ (immutable)   │ (orchestration)         │ (mutable artifacts)   │
│ Policy        │ Stage state machine     │ products/<id>/        │
│ Budget        │ Scaffold / codegen      │   spec/ src/ tests/   │
│ Audit         │ Test orchestrator       │   runs/ metrics/      │
│ Secrets broker│ Mutation applicator     │   changelog/          │
│ Tool broker   │ Selection / fitness     │                       │
│ Sandbox ctrl  │ Scheduler / monitor     │                       │
└───────────────┴─────────────────────────┴───────────────────────┘
                             │
┌────────────────────────────┴────────────────────────────────────┐
│  Adapters (infrastructure)                                      │
│  Model providers · FS/Git worktrees · SQLite/JSONL store        │
│  Container sandbox · HTTP allowlist client · Clock / cron       │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Trust boundary

```text
Untrusted:  model output, product code, product-requested tool args
Trusted:    kernel policy, budgets, secret material, audit, activation gates

Product code NEVER receives raw secrets.
Product code mutates ONLY under products/<id>/ (or staged worktrees).
Outbound I/O goes ONLY through the Tool Broker with policy + budget checks.
Default verification is offline (no network). Live tools require explicit policy.
```

### 2.3 Core domain objects

| Object | Meaning |
|---|---|
| `Idea` | Free-form human intent |
| `ProductSpec` | Normalized, versioned requirements and constraints |
| `Blueprint` | Modules, interfaces, tools needed, test plan, risks |
| `Product` | Durable identity for one living artifact line |
| `ProductVersion` | Immutable snapshot (code digest + evidence refs) |
| `Mission` | Lifecycle instance binding Idea → Product stages |
| `Evidence` | Test/sandbox/policy results for a version |
| `Observation` | Runtime health, cost, errors, quality signals |
| `MutationProposal` | Candidate change to a product workspace |
| `Fitness` | Multi-objective score used for selection |
| `Capability` | Named tool permission (not a raw credential) |

### 2.4 Lifelong stage machine

```text
idea_received
  → analyzing
  → designing
  → producing
  → verifying
  → activating          (local / scheduled only)
  → observing
  → improving           (mutate → verify → select)
  ↺ observing / improving for product lifetime
  → paused | archived
```

Failed verify returns to `producing` or `improving` with bounded retries.  
Circuit-open pauses the mission until explicit human resume.

### 2.5 Suggested repository layout (greenfield)

```text
product-brain/
  README.md
  docs/
    ARCHITECTURE.md          # this blueprint, evolved
    ROADMAP.md
    OPERATIONS.md
    thrIFT.md                # optional: threat model
  pyproject.toml             # or equivalent
  src/brain/
    kernel/                  # policy, budget, audit, secrets ports
    domain/                  # entities, value objects, errors
    application/             # use cases / orchestrators
    factory/                 # stage machine, scaffold, fitness
    tools/                   # tool broker + built-in capabilities
    sandbox/                 # execution profiles
    providers/               # model adapters
    store/                   # persistence
    interfaces/              # cli, api, ui
  products/                  # generated living products (gitignore runtime state)
  tests/
  .env.example
```

Keep `src/brain/kernel/**` non-mutable by the factory.  
Products live under `products/` and are the only lifelong mutation target by default.

---

## 3. Phased roadmap

### Brain v0 — Intelligent host (no free product factory yet)

**Goal:** a trustworthy brain that can accept an idea, structure it, plan work,
call a model under budget, and refuse unsafe actions — without generating and
running arbitrary products yet.

| Deliverable | Done when |
|---|---|
| Immutable kernel (policy, budget, audit) | External actions default-deny; secrets never leave broker |
| Idea → ProductSpec pipeline | Spec schema validated; clarification/defaults recorded |
| Model provider port | At least one provider; redacted audit of calls |
| Local CLI + minimal UI | Submit idea, view spec, view audit |
| Offline test suite | Kernel/policy/budget/spec tests pass without network |
| Docs: architecture + threat notes | Boundaries explicit |

**Exit criteria:** you can submit any idea and receive a structured spec + plan;
nothing executes product code or live tools yet.

**Reuse from EVO (optional patterns only):** policy prefixes, budget ledger,
JSONL audit, provider adapters, localhost UI discipline.

---

### Factory v1 — Idea → first product version

**Goal:** the brain can design, scaffold, generate, and verify a first product
version in an isolated workspace.

| Deliverable | Done when |
|---|---|
| Mission state machine | Stages persist; illegal transitions fail closed |
| Blueprint artifact | Modules, interfaces, required capabilities, test plan |
| Scaffold + codegen into `products/<id>/` | Multi-file project created in worktree |
| Offline verify profile | Sandbox runs allowlisted tests with no network |
| Evidence package | Pass/fail, digests, policy decisions stored |
| Activate locally | Human or policy-gated “activate this version” |
| Tool broker (stub + filesystem/test tools) | Products request capabilities by name |
| Mission CLI/UI | Create, advance, inspect evidence |

**Exit criteria:** for an arbitrary simple idea (e.g. CLI utility, local API,
static report job), Factory produces a tested local product version end-to-end.

**Still out of scope in v1:** open internet, continuous self-improvement loop,
multi-product populations, cloud deploy.

---

### Lifelong products v2 — Mutate, improve, monitor forever

**Goal:** activated products keep improving under observation, budgets, and
gates for their entire lifetime.

| Deliverable | Done when |
|---|---|
| Observation collectors | Errors, latency, cost, quality hooks per run |
| Improvement backlog | Observations → ranked mutation candidates |
| Mutation → verify → select loop | Only evidence-backed versions activate |
| Per-product schedules | Cron-like jobs owned by operations plane |
| Per-product budgets + circuit breaker | Exhaustion defers; failures pause with resume phrase |
| Optional live tool profile | Allowlisted egress; never default; budgeted |
| Multi-product registry | Many products, isolated workspaces, shared brain |
| Dashboard | Health, versions, spend, last mutations |

**Exit criteria:** after activation, a product can run on a schedule, gather
observations, propose mutations, verify them offline (and optionally live-probe),
and activate better versions without rewriting the kernel.

---

## 4. Cross-cutting invariants (all phases)

1. Kernel, secrets, policy, and audit are not product-mutable.  
2. Default verify = offline, credential-free, network-none.  
3. Live I/O only via Tool Broker + explicit capability grants.  
4. Activation ≠ cloud deployment; deployment remains an external operator concern.  
5. Payments, account creation, and identity bypass remain denied.  
6. All model and tool I/O is audited and size-bounded.  
7. Every activated version has reproducible evidence references.  
8. One active improver host per product (no split-brain writers).

---

## 5. Capability model (domain-agnostic)

Capabilities are **named permissions**, not domain features:

| Capability example | Typical use |
|---|---|
| `fs.read_product` | Read own workspace |
| `fs.write_product` | Write own workspace (staged) |
| `test.run` | Execute allowlisted verifier |
| `model.complete` | Ask brain/model via broker |
| `net.fetch` | Allowlisted HTTP (v2 optional) |
| `schedule.register` | Register recurring job (v2) |
| `metrics.write` | Emit observations |

A Blueprint declares required capabilities. Policy grants a subset. Products
never see the underlying API keys.

---

## 6. Fitness (generic, not domain-specific)

Multi-objective vector examples (weights are configurable):

- **Validity** — builds, schema, contracts  
- **Safety** — policy compliance, sandbox success  
- **Reliability** — flake rate, error budget  
- **Efficiency** — token/HTTP/time cost  
- **Novelty / improvement** — meaningful delta vs prior version  
- **Spec coverage** — acceptance checks mapped to ProductSpec  

Domain metrics (accuracy of forecasts, game score, etc.) are **product-defined
plugins**, not brain core.

---

## 7. Bootstrap checklist (new repo)

1. Create empty repo with layout in §2.5.  
2. Implement Brain v0 kernel + Idea→Spec only.  
3. Lock invariants with tests before Factory codegen.  
4. Add Factory v1 scaffold/verify/activate.  
5. Only then enable Lifelong v2 observe/mutate loop.  
6. Add live `net.fetch` last, behind allowlists and budgets.  
7. Keep bilingual/ops/UI polish as interface work, not domain logic.

---

## 8. Relationship to EVO Terrarium

| EVO Terrarium | Product Brain |
|---|---|
| Evolves organisms / code in a research dish | Births and evolves arbitrary products |
| Mutable default: `organisms/` | Mutable default: `products/<id>/` |
| Ecology metaphors (energy, niches) | Optional later; not required for v0–v2 |
| Strong existing promotion/trust stack | Reuse patterns; redesign around Mission/Product |

You may start Product Brain as a **sibling repository**. Do not weaken EVO’s
terrarium invariants to force this vision into the current tree unless you
explicitly fork and rebrand.

---

## 9. Phase summary

| Phase | One-line outcome |
|---|---|
| **Brain v0** | Trusted idea intake + planning brain |
| **Factory v1** | Idea → designed, built, verified local product |
| **Lifelong v2** | Products self-improve and are monitored for life |
