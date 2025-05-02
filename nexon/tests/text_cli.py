import pytest
import os
import subprocess
from pathlib import Path

from typer.testing import CliRunner
from nexon_cli.cli import cli
from nexon_cli.utils.paths import *


@pytest.fixture(autouse=True)
def temp_nexon_home(tmp_path, monkeypatch):
    # Point Nexon at a fresh temp directory
    monkeypatch.setattr("pathlib.Path.home", lambda cls=None: tmp_path)
    assert Path.home() == tmp_path


runner = CliRunner()


def test_create_and_list_envs_cli():
    # Create an environment
    result = runner.invoke(cli, ["create-env", "cli_env", "--role", "tester"])
    assert result.exit_code == 0
    # Verify the YAML file was created
    env_file = ENVIRONMENTS_DIR / "cli_env.yaml"
    assert env_file.exists()
    # List environments
    result = runner.invoke(cli, ["list-envs"])
    assert "cli_env" in result.stdout

def test_create_and_list_packages_cli():
    # Scaffold a package
    result = runner.invoke(cli, ["create-package", "cli_pkg", "--version", "0.5.0"])
    assert result.exit_code == 0
    # Verify package directory and spec
    pkg_dir = PACKAGES_DIR / "cli_pkg" / "0.5.0"
    assert (pkg_dir / "package.yaml").exists()
    # List packages
    result = runner.invoke(cli, ["list-packages"])
    assert "cli_pkg: 0.5.0" in result.stdout

def test_install_package_dry_run_and_actual(monkeypatch):
    # Create a simple package A
    pkgA = PACKAGES_DIR / "A" / "1.0.0"
    pkgA.mkdir(parents=True)
    (pkgA / "package.yaml").write_text("""
name: A
version: 1.0.0
requires: []
env: {}
build: {}
commands: {}
""")
    # Create environment
    runner.invoke(cli, ["create-env", "cli_env2"])
    # Dry-run install
    result = runner.invoke(cli, ["install-package", "cli_env2", "A>=1.0", "--dry-run"])
    assert result.exit_code == 0
    assert "+ A-1.0.0" in result.stdout
    # Actual install
    result = runner.invoke(cli, ["install-package", "cli_env2", "A>=1.0"])
    assert result.exit_code == 0
    assert "✅ Installation complete" in result.stdout

def test_diff_env_cli():
    # Create two environments
    runner.invoke(cli, ["create-env", "d1"])
    runner.invoke(cli, ["create-env", "d2"])
    # Manually set package lists
    env1 = ENVIRONMENTS_DIR / "d1.yaml"
    env2 = ENVIRONMENTS_DIR / "d2.yaml"
    env1.write_text("name: d1\npackages: [X-1.0.0]\nrole: r1\n")
    env2.write_text("name: d2\npackages: [X-1.0.0, Y-2.0.0]\nrole: r2\n")
    # Diff command
    result = runner.invoke(cli, ["diff-env", "d1", "d2"])
    assert result.exit_code == 0
    assert "+ Y-2.0.0" in result.stdout
    assert "Role changed: r1 → r2" in result.stdout

def test_wrap_tool_and_install_cli():
    # Create a dummy tool directory with an executable
    src_dir = Path(BASE_DIR) / "dummy_tool"
    src_dir.mkdir()
    script = src_dir / "run.sh"
    script.write_text("#!/bin/sh\necho hello")
    script.chmod(0o755)
    # Wrap tool
    result = runner.invoke(cli, ["wrap-tool", str(src_dir), "--name", "dummy", "--version", "0.0.1"])
    assert result.exit_code == 0
    assert "dummy-0.0.1" in result.stdout
    # Install wrapped tool
    runner.invoke(cli, ["create-env", "cli_env3"])
    result = runner.invoke(cli, ["install-package", "cli_env3", "dummy-0.0.1"])
    assert result.exit_code == 0
    assert "dummy-0.0.1" in result.stdout

def test_build_package_cli(monkeypatch):
    # Scaffold a buildable package
    pkg = PACKAGES_DIR / "Z" / "0.1.0"
    pkg.mkdir(parents=True)
    (pkg / "package.yaml").write_text("""
name: Z
version: 0.1.0
requires: []
env: {}
build:
  commands:
    - echo built Z
commands: {}
""")
    # Build command
    result = runner.invoke(cli, ["build-package", "Z", "0.1.0"])
    assert result.exit_code == 0
    assert "✅ Package built: Z-0.1.0" in result.stdout

def test_build_docker_cli(monkeypatch):
    # Create environment for Docker
    runner.invoke(cli, ["create-env", "cli_env4"])
    # Stub docker build
    called = {"docker": False}
    def fake_run(cmd, check):
        if "docker" in cmd:
            called["docker"] = True
        return None
    monkeypatch.setattr(subprocess, "run", fake_run)
    result = runner.invoke(cli, ["build-docker", "cli_env4", "--tag", "test/cli_env4:latest"])
    assert result.exit_code == 0
    assert "✅ Docker image built: test/cli_env4:latest" in result.stdout
    assert called["docker"]
