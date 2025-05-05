# tests/test_integration.py

import os
import tempfile
import threading
import time
import shutil

import pytest
from pathlib import Path
from typer.testing import CliRunner
from fastapi.testclient import TestClient

# ─── Fixture: Set up isolated Nexon home & DB ─────────────────────────────────


@pytest.fixture(scope="session", autouse=True)
def isolated_env(tmp_path_factory, monkeypatch):
    # 1) Create a temp “home” for the CLI
    home = tmp_path_factory.mktemp("nexon_home")
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{home/ 'nexon.db'}")
    monkeypatch.setenv("JWT_SECRET", "testsecret")
    # Override CLI base_dir and subdirs
    from nexon_cli.core.config import config as cli_cfg
    monkeypatch.setattr(cli_cfg, "base_dir", home)
    monkeypatch.setattr(cli_cfg, "environments_dir", home/"environments")
    monkeypatch.setattr(cli_cfg, "packages_dir",     home/"packages")
    monkeypatch.setattr(cli_cfg, "recipes_dir",      home/"recipes")
    # Ensure directories exist
    for d in ("environments_dir","packages_dir","recipes_dir"):
        getattr(cli_cfg, d).mkdir(parents=True, exist_ok=True)

    # 2) Initialize the database via Alembic
    #    (requires alembic config to read DATABASE_URL from env)
    from subprocess import run
    run(["alembic", "upgrade", "head"], check=True)

    return home


# ─── Fixture: CLI runner & TestClient ────────────────────────────────────────

@pytest.fixture(scope="session")
def cli_runner():
    return CliRunner()


@pytest.fixture(scope="session")
def api_client(isolated_env):
    # Delay import until after env is set
    from app.main import app
    client = TestClient(app)
    return client


# ─── 1) CLI Smoke Tests ──────────────────────────────────────────────────────

def test_cli_basic_env_pkg(cli_runner):
    # Create & list env
    res = cli_runner.invoke(cli_runner.test_cli or __import__("nexon_cli.cli").cli, ["create-env","it_env","--role","qa"])
    assert res.exit_code == 0
    assert "it_env.yaml" in os.listdir(os.environ["HOME"] + "/.nexon/environments") or "it_env" in res.stdout

    res = cli_runner.invoke(__import__("nexon_cli.cli").cli, ["list-envs"])
    assert res.exit_code == 0
    assert "it_env" in res.stdout

    # Create & list package
    res = cli_runner.invoke(__import__("nexon_cli.cli").cli, ["create-package","it_pkg","--version","1.2.3"])
    assert res.exit_code == 0

    res = cli_runner.invoke(__import__("nexon_cli.cli").cli, ["list-packages"])
    assert "it_pkg: 1.2.3" in res.stdout


# ─── 2) API Smoke Tests ──────────────────────────────────────────────────────

def test_api_endpoints(api_client):
    # Auth token
    token_resp = api_client.post("/auth/token", data={"username":"admin","password":"wrong"})
    assert token_resp.status_code == 401

    # Workaround: bypass auth for smoke-testing healthcheck
    health = api_client.get("/").json()
    assert health["status"] == "ok"
    assert "version" in health

    # Envs endpoint
    # create an env via CLI for API to list
    from subprocess import run
    run(["nexon","create-env","web_env","--role","web"])
    res = api_client.get("/envs", headers={"Authorization":"Bearer wrong"})
    assert res.status_code == 401


# ─── 3) Mixed CLI + API Flow ─────────────────────────────────────────────────

def test_mixed_install_and_lock(cli_runner, api_client):
    # Scaffold a dummy package
    home = Path(os.environ["NEXON_BASE_DIR"])
    pkgdir = home/"packages"/"DUMMY"/"9.9.9"
    pkgdir.mkdir(parents=True)
    (pkgdir/"package.yaml").write_text("""
name: DUMMY
version: 9.9.9
requires: []
env: {}
build: {}
commands: {}
""")

    # Install into env
    cli_runner.invoke(__import__("nexon_cli.cli").cli, ["install-package","it_env","DUMMY-9.9.9"])
    # Lock env
    cli_runner.invoke(__import__("nexon_cli.cli").cli, ["lock-env","it_env"])
    # Diff env and lockfile via API
    data = api_client.post("/api/graph/", json={"requirements":["DUMMY>=9.9"]})
    assert data.status_code == 200
    graph = data.json()
    assert "DUMMY-9.9.9" in graph

