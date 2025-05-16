import os.path

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, envs, packages, audit, metrics
from app.routers.assets import router as assets_router
from app.routers.notifications import router as notif_router
from app.routers import (
    auth_tokens,
    licenses,
    marketplace,
    preview,
    developer
)
from app.config import settings

app = FastAPI(title="Nexon Central API", version="0.1.0")

# Mount the 'static' directory under '/static'
# Adjust the path to point at the sibling 'nexon_web/static' folder:
static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "nexon_web", "static"))
app.mount("/static", StaticFiles(directory=static_dir), name="static")

static_preview = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "nexon_web_preview", "static"))
app.mount("/preview/static", StaticFiles(directory=static_preview), name="preview_static")
app.mount("/preview/manifest.json", StaticFiles(directory=os.path.dirname(static_preview)),
          name="preview_manifest")

# Auth
app.include_router(auth.router)

# CRUD routers
app.include_router(envs.router)
app.include_router(packages.router)
app.include_router(audit.router)
app.include_router(metrics.router)
app.include_router(assets_router)
app.include_router(notif_router)
app.include_router(auth_tokens.router)
app.include_router(licenses.router)
app.include_router(marketplace.router)
app.include_router(preview.router)
app.include_router(developer.router)


# Root healthcheck
@app.get("/")
def health():
    return {"status": "ok", "version": settings.VERSION}
