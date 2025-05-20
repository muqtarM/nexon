import os
import pytest
from fastapi.testclient import TestClient

from nexon_server.app.main import app
from nexon_server.app.core.tenant_manager import TenantManager
from nexon_server.app.db import SessionLocal
from app.routers.envs import router as envs_router
from app.routers.auth import get_current_user

# Mount test client
client = TestClient(app)


@pytest.fixture(autouse=True)
def setup_tenants(monkeypatch):
    # stub out get_current_user to always return an admin
    monkeypatch.setattr("app.routers.auth.get_current_user",
                        lambda: {"username": "admin", "role": "admin"})
    yield


def create_env(tenant, name):
    # Use the /t/{tenant}/... prefix
    resp = client.post(f"/t/{tenant}/envs",
                       json={"name": name, "role": "dev"})
    assert resp.status_code == 200
    return resp.json()


def list_envs(tenant):
    resp = client.get(f"/t/{tenant}/envs")
    assert resp.status_code == 200
    return resp.json()

def test_api_envs_isolation(tmp_path, monkeypatch):
    # ensure the DB uses a temp file or separate in-memory DB per tenant
    # override DATABASE_URL for tests (e.g. sqlite:///:memory:)
    monkeypatch.setenv("DATABASE_URL", "sqlite:///./test.db")
    # recreate tables
    from alembic import command
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    # Tenant "studio1" creates an env
    e1 = create_env("studio1", "shot01")
    assert e1["name"] == "shot01"
    # Tenant "studio2" sees no envs
    envs2 = list_envs("studio2")
    assert envs2 == []

    # studio2 creates its own
    create_env("studio2", "shot02")
    envs2b = list_envs("studio2")
    assert [e["name"] for e in envs2b] == ["shot02"]

    # studio1 still only has shot01
    envs1 = list_envs("studio1")
    assert [e["name"] for e in envs1] == ["shot01"]
