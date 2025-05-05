from fastapi import FastAPI
from app.routers import auth, envs, packages, audit, metrics
from app.routers.assets import router as assets_router
from app.config import settings

app = FastAPI(title="Nexon Central API", version="0.1.0")

# Auth
app.include_router(auth.router)

# CRUD routers
app.include_router(envs.router)
app.include_router(packages.router)
app.include_router(audit.router)
app.include_router(metrics.router)
app.include_router(assets_router)


# Root healthcheck
@app.get("/")
def health():
    return {"status": "ok", "version": settings.VERSION}
