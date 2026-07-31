# EVO Terrarium Local UI

The v0.3 UI includes a Digital Petri Dish observatory. It displays ecological
epoch, living population, births, extinctions, carrying capacity, mean energy,
mean fitness, a scrollable SVG parent-child lineage map, and a ranked living
organism roster. English remains the default language and every new label has a
fluent Persian translation.

The v0.4 observatory adds environmental resource meters, the current selection
phase, behaviour-derived niche counts, and a bounded cooperation network. These
views describe simulation state only and do not imply external agent activity.

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
