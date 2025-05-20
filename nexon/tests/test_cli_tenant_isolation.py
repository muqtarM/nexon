import os
import shutil
from pathlib import Path
import pytest
from typer.testing import CliRunner

from nexon_cli.cli import cli as cli_app
from nexon_cli.core.configs import config
from nexon_cli.core.tenant_manager import CLITenantManager


runner = CliRunner()


@pytest.fixture(autouse=True)
def isolate_base(tmp_path, monkeypatch):
    # each tenant gets its own NEXON_BASE_DIR under tmp_path
    base = tmp_path / "nexon_home"
    monkeypatch.setenv("NEXON_BASE_DIR", str(base))
    yield
    # cleanup
    shutil.rmtree(str(base), ignore_errors=True)


def run_cmd(tenant, *args):
    """Helper to invoke CLI with --tenant"""
    return runner.invoke(cli_app, ["--tenant", tenant, *args])


def test_create_env_per_tenant(tmp_path):
    # Tenant "alpha" creates an env and installs a package
    res1 = run_cmd("alpha", "create-env", "env1", "--role", "dev")
    assert res1.exit_code == 0
    res2 = run_cmd("alpha", "list-envs")
    assert "env1" in res2.stdout

    # Tenant "beta" has no envs yet
    res3 = run_cmd("beta", "list-envs")
    assert "No environments" in res3.stdout or "env1" not in res3.stdout

    # Creating same env name under beta is allowed
    res4 = run_cmd("beta", "create-env", "env1", "--role", "artist")
    assert res4.exit_code == 0
    res5 = run_cmd("beta", "list-envs")
    assert "env1" in res5.stdout


def test_lock_and_diff_per_tenant(tmp_path):
    # alpha creates and locks
    run_cmd("alpha", "create-env", "envA", "--role", "qa")
    run_cmd("alpha", "lock-env", "envA")
    # beta has no lockfile
    res = run_cmd("beta", "diff-env", "envA", "envA.lock.yaml")
    assert res.exit_code != 0  # should error or show nothing

    # beta locks its own envA
    run_cmd("beta", "lock-env", "env1")
    res2 = run_cmd("beta", "diff-env", "env1", "env1.lock.yaml")
    assert res2.exit_code == 0
