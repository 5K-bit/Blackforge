from fastapi import FastAPI

app = FastAPI(title="{{ project_name }}")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "hud": "{{ project_name }}"}


@app.get("/")
def root() -> dict[str, str]:
    return {"name": "{{ project_name }}", "surface": "obeos-hud"}
