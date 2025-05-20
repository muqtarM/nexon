import shutil
import tempfile
from pathlib import Path
import pytest

from nexon_cli.core.plugin_lifecycle import PluginLifecycleManager, PluginLifecycleError


@pytest.fixture
def temp_plugin_dir(tmp_path):
    # Create a fake plugin folder with plugin.yaml
    p = tmp_path / "my_plugin"
    p.mkdir()
    (p / "plugin.yaml").write_text("name: my_plugin\nversion: 0.1.0\ndescription: test")
    return p


def test_install_from_path(temp_plugin_dir, tmp_path, monkeypatch):
    # Point base_dir to a temp location
    base = tmp_path / "nexon_home"
    monkeypatch.setenv("NEXON_BASE_DIR", str(base))
    mgr = PluginLifecycleManager()
    # Install
    name = mgr.install_from_path(str(temp_plugin_dir))
    assert name == "my_plugin"
    installed = base / "plugins" / "my_plugin"
    assert installed.exists()
    # Installing again should error
    with pytest.raises(PluginLifecycleError):
        mgr.install_from_path(str(temp_plugin_dir))


def test_list_and_uninstall(tmp_path, monkeypatch):
    base = tmp_path / "nexon_home"
    monkeypatch.setenv("NEXON_BASE_DIR", str(base))
    mgr = PluginLifecycleManager()
    # Create two dummy plugins
    for nm in ("p1", "p2"):
        d = base / "plugins" / nm
        d.mkdir(parents=True, exist_ok=True)
        (d / "plugin.yaml").write_text(f"name: {nm}\nversion: 0.0.1")
    plugins = mgr.list_plugins()
    assert {p["name"] for p in plugins} == {"p1", "p2"}
    # Uninstall p1
    mgr.uninstall_plugin("p1")
    assert not (base/"plugins"/"p1").exists()
    # Uninstall non-existent
    with pytest.raises(PluginLifecycleError):
        mgr.uninstall_plugin("nope")
