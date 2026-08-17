from fastapi import FastAPI

app = FastAPI(title="{{ project_name }}", version="0.1.0")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "component": "{{ project_name }}", "type": "service"}


@app.get("/ready")
def ready() -> dict[str, bool]:
    return {"ready": True}
