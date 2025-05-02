import os
from pathlib import Path
from typing import List, Dict, Optional

from nexon_cli.utils.file_ops import save_yaml, load_yaml
from nexon_cli.utils.logger import logger
from nexon_cli.utils.paths import ENVIRONMENTS_DIR, PACKAGES_DIR
from nexon_cli.core.dependency_solver import DependencySolver, DependencyError


class PackageManager:
    """
    Manage creation, listing, installation and removal of Nexon package
    """
    def __init__(self):
        """
        Ensure that the base directories for environments and packages exist.
        :return:
        """
        self.env_dir = ENVIRONMENTS_DIR.mkdir(parents=True, exist_ok=True)
        self.pkg_dir = PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
        self.solver = DependencySolver()

    def create_package(self, name: str, version: str = "0.1.0") -> None:
        """
        Scaffold a new custom package template in PACKAGES_DIR
        :param name:
        :param version:
        :return:
        """
        pkg_root = self.pkg_dir / name / version
        pkg_root.mkdir(parents=True, exist_ok=True)
        pkg_file = pkg_root / f"package.yaml"
        if pkg_file.exists():
            logger.warning(f"Package '{name}-{version}' already exists. Overwriting...")

        pkg_data = {
            "name": name,
            "version": version,
            "description": "",
            "requires": [],
            "env": {},
            "commands": {},
            "build": {},
            "tags": [],
            "platforms": ["windows", "linux", "macos"],
        }
        save_yaml(pkg_file, pkg_data)
        logger.success(f"Scaffold package: {name}-{version}")

    def list_packages(self) -> None:
        """
        List all package specs in PACKAGES_DIR.
        :return:
        """
        pkg_dirs = sorted(self.pkg_dir.iterdir()) if self.pkg_dir.exists() else []
        if not pkg_dirs:
            logger.warning("No packages found.")
            return

        logger.title("Available Packages")
        for pkg_dir in pkg_dirs:
            if not pkg_dir.is_dir():
                continue
            versions = sorted(
                [d.name for d in pkg_dir.iterdir() if d.is_dir()],
                key=lambda v: self.solver.pkg_defs.get(pkg_dir.name, []),
                reverse=True
            )
            for ver in versions:
                pkg_file = pkg_dir/ ver / "package.yaml"
                if not pkg_file.exists():
                    continue
                meta = load_yaml(pkg_file)
                tags = ", ".join(meta.get("tags", []))
                print(f"- {meta['name']}-{meta['version']} ({tags})")

    def install_package(self, env_name: str, requirement: str):
        """
        Install a package and its dependencies into an environment.
        requirement can be 'name', 'name-version', or 'name>=x,<y'.
        """
        env_file = self.env_dir / f"{env_name}.yaml"

        if not env_file.exists():
            logger.error(f"Environment '{env_name}' not found.")
            return

        # Resolve package-version list
        try:
            pkgvers = self.solver.resolve([requirement])
        except DependencyError as e:
            logger.error(f"Dependency resolution error: {e}")
            return

        env_data = load_yaml(env_file)
        installed: List[str] = env_data.get("packages", [])
        added = []
        for pv in pkgvers:
            if pv not in installed:
                installed.append(pv)
                added.append(pv)
        env_data["packages"] = installed
        save_yaml(env_file, env_data)

        if added:
            logger.success(f"Installed into '{env_name}': {', '.join(added)}")

        return added

    def uninstall_package(self, env_name: str, pkgver: str) -> None:
        """
        Remove a specific package-version from an environment
        :param env_name:
        :param pkgver:
        :return:
        """
        env_file = self.env_dir / f"{env_name}.yaml"
        if not env_file.exists():
            logger.error(f"Environment '{env_name}' not found.")

        env_data = load_yaml(env_file)
        installed: List[str] = env_data.get("packages", [])
        if pkgver not in installed:
            logger.warning(f"Package '{pkgver}' is not installed in '{env_name}'.")
            return

        installed.remove(pkgver)
        env_data["packages"] = installed
        save_yaml(env_file, env_data)
        logger.success(f"Uninstalled package '{pkgver}' from environment '{env_name}'.")

    def resolve_package_env_vars(self, package_list: List[str]) -> Dict[str, str]:
        """
        Aggregate all 'env' blocks from each package version into a single dict
        """
        merged = {}
        for pv in package_list:
            try:
                name, ver = pv.rsplit('-', 1)
            except ValueError:
                continue
            pkg_file = self.pkg_dir / name / ver / "package.yaml"
            if not pkg_file.exists():
                logger.warning(f"Spec missing for '{pv}'")
                continue
            meta = load_yaml(pkg_file)
            for key, val in meta.get("env", {}).items():
                if key in merged:
                    # prepend new value for path-like vars
                    merged[key] = f"{val}{Path(os.pathsep).exists() and os.pathsep or ':'}{merged[key]}"
                else:
                    merged[key] = val
        return merged
