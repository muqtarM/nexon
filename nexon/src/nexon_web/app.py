from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from nexon_web.routers import envs, packages, graph
from nexon_web.metrics import router as metrics_router

app = FastAPI(title="Nexon Dashboard API", version="0.1.0")

# 1. Cors middleware (allow your front-end to talk to this API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],        # TODO: lock this down in prod
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Mount API routers
app.include_router(envs.router,     prefix="/api/envs",     tags=["Environments"])
app.include_router(packages.router, prefix="/api/packages", tags=["Packages"])
app.include_router(graph.router,    prefix="/api/graph",    tags=["Graph"])

# Mount metrics at /metrics
app.include_router(metrics_router, tags=["Metrics"])

# 3. Serve static frontend assets (e.g. React/Svelte build) from /
app.mount(
    "/",
    StaticFiles(directory=Path(__file__).parent / "static", html=True),
    name="static"
)
