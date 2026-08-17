# BlackForge

[![CI](https://github.com/5K-bit/Blackforge/actions/workflows/ci.yml/badge.svg)](https://github.com/5K-bit/Blackforge/actions/workflows/ci.yml)

BlackForge is the local-first OBEOS development toolchain. It turns repeatable architecture into reusable, validated component scaffolds so new OBEOS software starts from a known contract instead of copied boilerplate.

## OBEOS component templates

- `obeos-service` — FastAPI service with health/readiness contracts and tests.
- `obeos-agent` — bounded async agent request/result contract.
- `obeos-skill` — load-on-demand Markdown skill contract.
- `obeos-worker` — bounded background job processor.
- `obeos-connector` — external-system integration boundary.
- `obeos-device` — hardware/device adapter boundary.
- `obeos-event-consumer` — explicit event-processing entrypoint.
- `obeos-hud` — thin FastAPI UI/status surface.

General templates remain available: `cli`, `fastapi`, and `python-package`.

Every OBEOS scaffold includes `obeos.manifest.json`, using schema version 1 and the canonical `component_type` field. The manifest is the stable discovery boundary for OBEOS registries, launchers, health tooling, and adapters without coupling generated components to DAISE internals.

## Installation

```bash
pip install -e ".[dev]"
```

## Create components

```bash
blackforge list-templates
blackforge new obeos-service sentinel-bridge
blackforge new obeos-agent research-agent
blackforge new obeos-worker queue-worker
blackforge new obeos-connector telegram-bridge
blackforge new obeos-device mesh-node
blackforge new obeos-event-consumer audit-consumer
blackforge new obeos-hud legion-hud
blackforge new obeos-skill weekly-review
```

The generic command works for every installed template:

```bash
blackforge create TEMPLATE PROJECT_NAME
```

Preview a generation plan without touching disk:

```bash
blackforge create obeos-agent planner-agent --preview
```

BlackForge rejects path traversal and nested project-name paths. Existing destinations are protected unless `--force` is explicitly supplied.

## Inspect and validate OBEOS components

From a generated component:

```bash
blackforge inspect .
blackforge validate obeos.manifest.json
blackforge doctor .
```

`inspect` discovers the nearest manifest by walking parent directories. `validate` checks the OBEOS manifest contract. `doctor` checks the local Python/tooling/component environment.

## Manifest contract

Schema version 1 requires:

- `schema_version`
- `name`
- `component_type`
- `version`
- `entrypoint`

Components can additionally declare interfaces, package name, health/readiness endpoints, and generation metadata.

## Development

```bash
pytest
```

CI tests Python 3.11 and 3.12.

## Source-of-truth policy

`5K-bit/Blackforge` is the canonical BlackForge repository. The `Blackforge` path inside the O.B.E.O.S. repository should reference this repository as a pinned Git submodule rather than maintain an independent copy. Changes belong here first; OBEOS then advances the pinned commit after BlackForge CI passes.
