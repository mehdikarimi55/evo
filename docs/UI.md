# EVO Terrarium Local UI

The UI includes a Digital Petri Dish observatory. It displays ecological
epoch, living population, births, extinctions, carrying capacity, mean energy,
mean fitness, a fully navigable SVG parent-child lineage map (all generations,
with scrollbars, wheel zoom, and hand-drag panning), and a ranked living
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

The Digital Petri Dish ecology cards (resources, niches, cooperation) and the
lineage map are independently collapsible and start collapsed. Ecology cards,
resource meters, niche chips, cooperation links, and the lineage graph use a
higher-contrast light blue/gray observatory treatment so population state stays
readable at a glance.

The Evolution Journal includes a **Read journey** action on each timeline
entry. It opens a modal with a bilingual storytelling chronicle of the
evolution path from the first recorded moment through that entry. The story is
composed from the public journal only and never exposes credentials or raw
patches. In Persian mode, UI chrome uses built-in FA templates, and Latin
proposal fields (objective, summary, rationale, benefit, risk) are translated
via the configured model provider into a local cache at `.evo/i18n-cache-fa.json`
so later journal/journey views reuse the same Persian text.

Main workspace panels (Life Support, Environment Controls, Manual Selection,
Open-Ended Loop, Digital Petri Dish, Evidence Integrity, Evolution Journal, and
Audit trail) are also `<details>` sections: collapsed by default, expandable via
the panel header. Global search stays available in the Audit summary without
toggling the panel, and matching panels open automatically while filtering.

Hover help appears on panels, ecology cards, pipeline cards, status/metric chips,
achievements, organism cards, and journey summary elements. Descriptions are
bilingual (EN/FA) and follow the selected UI language. Organism roster cards and
lineage nodes show a per-gnome summary (lineage, generation, role, energy,
fitness, parents, adaptations, and collaboration counts).

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
| NVIDIA models | Dropdown catalog (merged with live `/models` when available) |
| Groq models | Dropdown catalog (merged with live `/models` when available) |
| NVIDIA generation profile | Precise / balanced / exploratory decoding controls |
| Doctor | Validates host configuration |
| Probe | One provider health request |
| Evolve | One bounded generation through the immutable kernel |
| Audit search | Filters redacted `.evo/audit.jsonl` events |
| Global search | Filters visible panels and audit rows in the page |
| Evolution journey | Large colorful modal with synopsis, stats, and timeline chapters; full Persian RTL when FA is selected, including cached translation of proposal free-text |
| Achievements | Host catalog from `GET /api/achievements`; UI count is unlocked / catalog total |
| Hover help | Mouse-over / focus tooltips on panels and cards describe each section in EN or FA |
| Lineage map | Large viewport (`min(48rem, 82vh)`); all generations with scroll, wheel-zoom, and hand-drag pan |

## Security notes

1. Credentials remain host-owned and are stored only in `.env.local`.
2. API responses expose `api_key: "configured"` at most.
3. Audit payloads use the same redaction rules as the CLI path.
4. Evolve still does not apply mutations to the repository in v0.1.
