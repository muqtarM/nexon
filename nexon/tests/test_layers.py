import pytest
import os
import yaml
from pathlib import Path
from typer.testing import CliRunner

from nexon_cli.cli import cli
from nexon_cli.core.configs import config


@pytest.fixture(autouse=True)
def temp_nexon_home(tmp_path, monkeypatch, tmp_path_factory):
    """
    Redirect Nexon home directories to a temporary path for isolation.
    Also run commands from a temp CWD so spec files are local.
    """
    # Set config directories
    monkeypatch.setattr(config, "base_dir", tmp_path)
    monkeypatch.setattr(config, "layers_dir", tmp_path / "layers")
    monkeypatch.setattr(config, "environments_dir", tmp_path / "environments")
    monkeypatch.setattr(config, "packages_dir", tmp_path / "packages")
    monkeypatch.setattr(config, "recipes_dir", tmp_path / "recipes")
    # Ensure directories exist
    for attr in ("layers_dir", "environments_dir", "packages_dir", "recipes_dir"):
        getattr(config, attr).mkdir(parents=True, exist_ok=True)
    # Change cwd to a new temp dir for spec files
    spec_dir = tmp_path / "specs"
    spec_dir.mkdir()
    monkeypatch.chdir(spec_dir)
    yield


runner = CliRunner()


def test_create_global_layer_and_list():
    # Run create-layer for global without pre-existing spec
    result = runner.invoke(cli, ["create-layer", "global", "global.yaml"])
    assert result.exit_code == 0
    # global.yaml spec should be created in cwd
    spec_path = Path.cwd() / "global.yaml"
    assert spec_path.exists()
    # ~/.nexon/layers/global.yaml should exist
    layer_path = config.base_dir / "layers" / "global.yaml"
    assert layer_path.exists()
    # List layers should show global
    result = runner.invoke(cli, ["list-layers"])
    assert "global" in result.stdout


def test_create_team_and_show_effective():
    # Prepare a simple environment file
    env_file = config.environments_dir / "shot01.yaml"
    env_file.write_text("name: shot01\npackages: [P1-1.0.0]\nrole: base\n")
    # Create team layer spec file
    team_spec = {
        "role": "fx",
        "packages": ["P2-2.0.0"]
    }
    with open("fx.yaml", "w") as f:
        yaml.safe_dump(team_spec, f)
    # Run create-layer for team
    result = runner.invoke(cli, ["create-layer", "team", "fx", "fx.yaml"])
    assert result.exit_code == 0
    # Show effective config for shot01, team=fx, project=proj1, user not provided
    result = runner.invoke(cli, ["show-effective", "shot01", "fx", "proj1"])
    assert result.exit_code == 0
    effective = yaml.safe_load(result.stdout)
    # Effective should include role fx (from team) and both packages merged
    assert effective["role"] == "fx"
    assert set(effective["packages"]) == {"P1-1.0.0", "P2-2.0.0"}


def test_project_and_user_layer_override():
    # Prepare env file
    env_file = config.environments_dir / "envA.yaml"
    env_file.write_text("name: envA\npackages: [A-1.0]\nrole: envRole\n")
    # Create project layer
    proj_spec = {"packages": ["B-1.0"], "env": {"X": "1"}}
    with open("proj1.yaml", "w") as f:
        yaml.safe_dump(proj_spec, f)
    runner.invoke(cli, ["create-layer", "project", "proj1", "proj1.yaml"])
    # Create user layer
    user_spec = {"packages": ["C-1.0"], "env": {"Y": "2"}}
    with open("alice.yaml", "w") as f:
        yaml.safe_dump(user_spec, f)
    runner.invoke(cli, ["create-layer", "user", "alice", "alice.yaml"])
    # Show effective with project and user
    result = runner.invoke(cli, ["show-effective", "envA", "teamX", "proj1", "--user", "alice"])
    assert result.exit_code == 0
    effective = yaml.safe_load(result.stdout)
    # Should include A-1.0, B-1.0, C-1.0
    assert set(effective["packages"]) == {"A-1.0", "B-1.0", "C-1.0"}
    # Env vars include X and Y
    assert effective["env"]["X"] == "1"
    assert effective["env"]["Y"] == "2"

