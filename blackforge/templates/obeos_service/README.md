# {{ project_name }}

Generated with BlackForge on {{ created_at }}.

OBEOS service scaffold with health/readiness endpoints, a manifest, and tests.

## Run

```bash
pip install -e ".[dev]"
uvicorn {{ package_name }}.main:app --reload
```

## Verify

```bash
pytest
```
