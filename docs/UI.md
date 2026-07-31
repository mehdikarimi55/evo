# EVO Terrarium Local UI

The UI includes a Digital Petri Dish observatory. It displays ecological
epoch, living population, births, extinctions, carrying capacity, mean energy,
mean fitness, a scrollable SVG parent-child lineage map, and a ranked living
organism roster. English remains the default language and every new label has a
fluent Persian translation.

The v0.4 observatory adds environmental resource meters, the current selection
phase, behaviour-derived niche counts, and a bounded cooperation network. These
views describe simulation state only and do not imply external agent activity.

The v0.5 evidence observatory adds ecological stability, population diversity,
an explicitly qualified open-endedness proxy, the latest cooperative team, and
the latest proposal-only/sandbox-verified state. All labels have fluent Persian
translations and remain usable in right-to-left mode.

The v0.6 Settings panel configures an optional rootless image, container engine,
evaluation command, and timeout. When autonomous evolution produces a valid
patch and the sandbox is enabled, the evidence observatory displays the
baseline comparison classification, changed paths, and promotion eligibility.
No UI action can merge or deploy the candidate.

The v0.7 gate exposes deterministic replay, a host-authenticated bundle, and a
local human assertion. The v0.8 public-trust observatory adds the Ed25519
authority fingerprint, trusted reviewer count, public attestation, independent
signed-review status, policy result, and manual-promotion authorization. The UI
may attest or authorize, but reviewer registration, private-key signing, and
revocation remain CLI-only operations. No browser request accepts private key
material or performs Git/deployment actions.

The v0.9 release observatory is read-only. It reports the latest sealed
candidate artifact, whether the independent authorization is current or
consumed, local repository cleanliness, the active local promotion, rollback
availability, and the permanent denial of deployment authority. Patch apply and
rollback are intentionally absent from the browser and require exact CLI
confirmation phrases.

The local UI is a stdlib HTTP console for host-side operations.

## Start

```bash
.venv/bin/evo ui --env-file .env.local
```

Defaults:

- host: `127.0.0.1`
- port: `8787`
- browser open: enabled

Useful flags:

- `--no-browser`
- `--host localhost`
- `--port 9000`

The server refuses non-localhost binds.

## Capabilities

| Area | Behavior |
|---|---|
| Settings | Writes `.env.local`; never returns raw API keys |
| Doctor | Validates host configuration |
| Probe | One provider health request |
| Evolve | One bounded generation through the immutable kernel |
| Audit search | Filters redacted `.evo/audit.jsonl` events |
| Global search | Filters visible panels and audit rows in the page |

## Security notes

1. Credentials remain host-owned and are stored only in `.env.local`.
2. API responses expose `api_key: "configured"` at most.
3. Audit payloads use the same redaction rules as the CLI path.
4. Evolve still does not apply mutations to the repository in v0.1.
