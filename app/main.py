from fastapi import FastAPI, status

from app.services.health import readiness

app = FastAPI(title="Resilient Mobile Wallet")


@app.get("/health")
async def health():
    # Liveness: process is up
    return {"status": "ok"}


@app.get("/ready")
async def ready():
    # Readiness: dependencies reachable
    r = await readiness()
    if not (r.postgres_ok and r.tigerbeetle_ok):
        return (
            {"ready": False, "postgres_ok": r.postgres_ok, "tigerbeetle_ok": r.tigerbeetle_ok},
            status.HTTP_503_SERVICE_UNAVAILABLE,
        )

    return {"ready": True, "postgres_ok": True, "tigerbeetle_ok": True}