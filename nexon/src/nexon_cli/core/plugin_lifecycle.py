import shutil
import subprocess
import yaml
from pathlib import Path

from nexon_cli.core.configs import config
from nexon_cli.utils.logger import logger


class PluginLifecycleError(Exception):
    pass


class PluginLifecycleManager:
    """
    Install, update, uninstall, and list Nexon plugins
    Plugins live under ~/.nexon/plugins/<plugin_name>, each with a plugin.yaml
    """

    def __init__(self):
        self.plugins_dir = Path(config.base_dir) / "plugins"
        self.plugins_dir.mkdir(parents=True, exist_ok=True)

    def list_plugins(self) -> list[dict]:
        """Return metadata from each installed plugin's plugin.yaml"""
        out = []
        for d in sorted(self.plugins_dir.iterdir()):
            if not d.is_dir():
                continue
            meta_file = d / "plugin.yaml"
            if not meta_file.exists():
                continue
            try:
                data = yaml.safe_load(meta_file.read_text(encoding="utf-8"))
                data["path"] = str(d)
                out.append(data)
            except Exception as e:
                logger.error(f"Failed to read plugin.yaml in {d}: {e}")
        return out

    def install_from_path(self, src_path: str) -> str:
        """
        Install a plugin by copying a local folder.
        Expects src_path/plugin.yaml to exist.
        """
        src = Path(src_path).expanduser()
        if not src.exists() or not src.is_dir():
            raise PluginLifecycleError(f"Path not found: {src}")
        name = src.name
        dest = self.plugins_dir / name
        if dest.exists():
            raise PluginLifecycleError(f"Plugin '{name}' is already installed")
        shutil.copytree(src, dest)
        logger.success(f"Installed plugin '{name}' from '{src}'")
        return name

    def install_from_git(self, git_url: str) -> str:
        """
        Install a plugin by `git clone`. Plugin name inferred from repo basename.
        """
        name = git_url.rstrip("/").split("/")[-1].removesuffix(".git")
        dest = self.plugins_dir / name
        if dest.exists():
            raise PluginLifecycleError(f"Plugin '{name}' is already installed")
        try:
            subprocess.run(["git", "clone", git_url, str(dest)], check=True)
        except subprocess.CalledProcessError as e:
            raise PluginLifecycleError(f"Git clone failed: {e}")
        logger.success(f"Installed plugin '{name}' from Git {git_url}")
        return name

    def update_plugin(self, name: str) -> str:
        """
        If plugin was installed via Git, do `git pull`. Otherwise reinstall.
        """
        pdir = self.plugins_dir / name
        if not pdir.exists():
            raise PluginLifecycleError(f"No such plugin '{name}'")
        git_dir = pdir / ".git"
        if git_dir.exists():
            try:
                subprocess.run(["git", "-C", str(pdir), "pull"], check=True)
                logger.success(f"Updated plugin '{name}' via Git pull")
                return name
            except subprocess.CalledProcessError as e:
                raise PluginLifecycleError(f"Git pull failed: {e}")
        else:
            raise PluginLifecycleError(f"Plugin '{name}' was not installed from a Git repo")

    def uninstall_plugin(self, name: str) -> None:
        """Remove a plugin directory entirely."""
        pdir = self.plugins_dir / name
        if not pdir.exists():
            raise PluginLifecycleError(f"No such plugin '{name}'")
        shutil.rmtree(pdir)
        logger.success(f"Uninstalled plugin '{name}'")
