# BlackForge

[![CI](https://github.com/5K-bit/Blackforge/actions/workflows/ci.yml/badge.svg)](https://github.com/5K-bit/Blackforge/actions/workflows/ci.yml)

BlackForge is a local-first development scaffolder for OBEOS and general Python projects. It turns repeatable architecture into reusable templates so new services, agents, skills, APIs, CLIs, and packages start with consistent structure instead of copied boilerplate.

## OBEOS Development Kit

BlackForge now ships with OBEOS-aware component templates:

- `obeos-service` — installable FastAPI service with health/readiness endpoints, tests, and an OBEOS manifest.
- `obeos-agent` — async agent contract with bounded request/result objects, tests, and an OBEOS manifest.
- `obeos-skill` — Markdown skill contract with explicit purpose, trigger, inputs, outputs, failure behavior, and recovery.

Generated OBEOS components include `obeos.manifest.json`. The manifest is the stable discovery boundary for future OBEOS registries, launchers, adapters, and orchestration without forcing generated projects to import the current DAISE internals.

## General Templates

- `cli`
- `fastapi`
- `python-package`

## Installation

```bash
pip install -e ".[dev]"
```

## Usage

List templates:

```bash
blackforge list-templates
```

Create OBEOS components:

```bash
blackforge new obeos-service sentinel-bridge
blackforge new obeos-agent research-agent
blackforge new obeos-skill weekly-review
```

Create general projects:

```bash
blackforge new cli my-tool
blackforge new fastapi my-api
blackforge new python-package my-package
```

Use the generic creator for any installed template:

```bash
blackforge create TEMPLATE PROJECT_NAME
```

Example:

```bash
blackforge create obeos-agent planner-agent
```

Overwrite an existing destination only when intentional:

```bash
blackforge new obeos-agent planner-agent --force
```

## OBEOS Manifest Contract

Every OBEOS scaffold declares at least:

- schema version
- component name and type
- version
- entrypoint
- supported interfaces
- generation timestamp

Services additionally declare health and readiness endpoints. This gives OBEOS a machine-readable registration surface while keeping each component independently testable.

## Development

Run tests:

```bash
pytest
```

The project targets Python 3.11+ and keeps runtime dependencies intentionally small.

## Direction

BlackForge should become the standard creation path for new OBEOS components. Future templates can cover workers, event consumers, HUD panels, connectors, device nodes, and deployment bundles while preserving the same manifest-first contract.
