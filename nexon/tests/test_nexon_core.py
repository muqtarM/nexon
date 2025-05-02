import os
import subprocess
import shutil
import yaml
import pytest
from pathlib import Path

from packaging.version import Version

from nexon_cli.utils import paths
from nexon_cli.core.env_manager import EnvironmentManager
from nexon_cli.core.package_manager import PackageManager
from nexon_cli.core.dependency_solver import DependencySolver, DependencyError
from nexon_cli.utils.file_ops import save_yaml, load_yaml
from nexon_cli.utils.shell_ops import set_environment_variables, reset_environment_variables
from nexon_cli.core.build_manager import BuildManager, BuildError
from nexon_cli.core.docker_builder import build_docker_image, DockerBuildError


@pytest.fixture(autouse=True)
def temp_nexon_home(tmp_path, monkeypatch):
    # Point Nexon at a fresh temp directory
    monkeypatch.setattr("pathlib.Path.home", lambda cls=None: tmp_path)
    # monkeypatch.setenv("HOME", str(tmp_path))
    # Path.home should now reflect temp_path
    assert Path.home() == tmp_path
    # monkeypatch.setattr(paths, "BASE_DIR", tmp_path)
    # monkeypatch.setattr(paths, "ENVIRONMENTS_DIR", tmp_path / "environments")
    # monkeypatch.setattr(paths, "PACKAGES_DIR", tmp_path / "packages")
    # monkeypatch.setattr(paths, "RECIPES_DIR", tmp_path / "recipes")
    # # ensure dirs
    # for d in ("ENVIRONMENTS_DIR", "PACKAGES_DIR", "RECIPES_DIR"):
    #     getattr(paths, d).mkdir(parents=True, exist_ok=True)
    # yield


def test_environment_lifecycle(tmp_path):
    em = EnvironmentManager()
    # Create
    em.create_environment("env1", role="test-role")
    env_file = paths.ENVIRONMENTS_DIR / "env1.yaml"
    assert env_file.exists()
    data = load_yaml(env_file)
    assert data["name"] == "env1"
    assert data["role"] == "test-role"
    # List
    listed = [f.stem for f in paths.ENVIRONMENTS_DIR.glob("*.yaml")]
    assert "env1" in listed
    # Lock
    em.lock_environment("env1")
    assert (paths.ENVIRONMENTS_DIR / "env1.lock.yaml").exists()
    # Activate / Deactivate (env-vars set/reset)
    # Prepare a dummy package to generate an env-var
    pkg_root = paths.PACKAGES_DIR / "P" / "1.0.0"
    pkg_root.mkdir(parents=True, exist_ok=True)
    save_yaml(pkg_root / "package.yaml", {
        "name":"P", "version":"1.0.0", "env":{"FOO":"bar"}
    })
    # inject package list
    data["packages"] = ["P-1.0.0"]
    save_yaml(env_file, data)
    # Activate
    em.activate_environment("env1")
    assert os.environ.get("NEXON_ENV") == "env1"
    assert os.environ.get("FOO") == "bar"
    # Deactivate
    em.deactivate_environment()
    assert os.environ.get("NEXON_ENV") is None or os.environ["NEXON_ENV"] != "env1"
    assert os.environ.get("FOO") is None

def test_dependency_solver_and_package_install(tmp_path):
    # Scaffold two packages A→B
    pkgA = paths.PACKAGES_DIR / "A" / "1.0.0"
    pkgA.mkdir(parents=True, exist_ok=True)
    save_yaml(pkgA / "package.yaml", {
        "name":"A","version":"1.0.0","requires":["B>=1.0"]
    })
    pkgB = paths.PACKAGES_DIR / "B" / "1.0.0"
    pkgB.mkdir(parents=True, exist_ok=True)
    save_yaml(pkgB / "package.yaml", {
        "name":"B","version":"1.0.0","requires":[]
    })

    solver = DependencySolver()
    # parse requirement
    name, spec = solver.parse_requirement("A>=1.0,<2.0")
    assert name == "A"
    assert ">=1.0" in str(spec)
    # list_versions
    vers = solver.list_versions("A")
    assert vers and vers[0] == Version("1.0.0")
    # resolve and resolve_all
    exact = solver.resolve("B-1.0.0")
    assert exact == "B-1.0.0"
    all_deps = solver.resolve_all(["A>=1.0"])
    assert set(all_deps) == {"A-1.0.0", "B-1.0.0"}
    # build_graph
    graph = solver.build_graph(["A>=1.0"])
    assert graph == {"A-1.0.0": ["B-1.0.0"], "B-1.0.0": []}

    # Test PackageManager install/uninstall/dry-run
    em = EnvironmentManager()
    em.create_environment("env2")
    pm = PackageManager()
    # Dry-run
    added = pm.install_package("env2", "A>=1.0", dry_run=True)
    assert set(added) == {"A-1.0.0","B-1.0.0"}
    data = load_yaml(paths.ENVIRONMENTS_DIR/"env2.yaml")
    assert data["packages"] == []  # no change

    # Actual install
    added2 = pm.install_package("env2", "A>=1.0")
    assert "A-1.0.0" in added2 and "B-1.0.0" in added2
    data2 = load_yaml(paths.ENVIRONMENTS_DIR/"env2.yaml")
    assert set(data2["packages"]) == set(added2)

    # Uninstall
    removed = pm.uninstall_package("env2", "B-1.0.0")
    assert removed == ["B-1.0.0"]
    data3 = load_yaml(paths.ENVIRONMENTS_DIR/"env2.yaml")
    assert "B-1.0.0" not in data3["packages"]

def test_wrap_tool(tmp_path):
    src = tmp_path/"mytoolsrc"
    src.mkdir()
    (src/"run.sh").write_text("#!/bin/sh\necho hello")
    pm = PackageManager()
    pkgver = pm.wrap_tool(str(src), name="mytool", version="2.3.4")
    assert pkgver == "mytool-2.3.4"
    pkg_root = paths.PACKAGES_DIR /"mytool"/"2.3.4"
    assert (pkg_root/"src"/"run.sh").exists()
    meta = load_yaml(pkg_root/"package.yaml")
    assert meta["name"] == "mytool" and meta["version"] == "2.3.4"
    # commands block should include 'run' (without extension) if run.sh is executable
    assert "run" in meta.get("commands",{})

def test_diff_environments_output(capsys):
    em = EnvironmentManager()
    em.create_environment("d1")
    em.create_environment("d2")
    # inject packages
    save_yaml(paths.ENVIRONMENTS_DIR /"d1.yaml", {"name":"d1","packages":["X-1.0.0"],"role":"r1"})
    save_yaml(paths.ENVIRONMENTS_DIR /"d2.yaml", {"name":"d2","packages":["X-1.0.0","Y-2.0.0"],"role":"r2"})
    em.diff_environments("d1","d2")
    out = capsys.readouterr().out
    assert "+ Y-2.0.0" in out
    assert "Role changed: r1 → r2" in out

def test_build_and_docker(monkeypatch):
    # Scaffold a trivial package with a build command
    pkg = paths.PACKAGES_DIR /"Z"/"0.1.0"
    pkg.mkdir(parents=True, exist_ok=True)
    save_yaml(pkg/"package.yaml", {
        "name":"Z","version":"0.1.0",
        "build":{"commands":["echo built Z"]},
        "env":{}, "requires":[], "commands":{}
    })
    bm = BuildManager()
    bm.build_package("Z","0.1.0")  # should run without exception

    # Create an empty env to Dockerize
    em = EnvironmentManager()
    em.create_environment("env3")
    # Monkeypatch subprocess.run to simulate docker build success
    monkeypatch.setattr(subprocess, "run", lambda *args, **kwargs: None)
    tag = build_docker_image("env3", tag="test/env3:latest")
    assert tag == "test/env3:latest"
