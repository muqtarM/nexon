import os
import shutil
from pathlib import Path
from typing import List, Dict

from packaging.version import Version, InvalidVersion
from nexon_cli.utils.file_ops import save_yaml, load_yaml
from nexon_cli.utils.logger import logger
from nexon_cli.utils.paths import ENVIRONMENTS_DIR, PACKAGES_DIR
from nexon_cli.core.dependency_solver import DependencySolver, DependencyError
from nexon_cli.core.plugin_manager import plugin_manager


class PackageManager:
    """
    Manage creation, listing, installation and removal of Nexon package
    """
    def __init__(self):
        """
        Ensure that the base directories for environments and packages exist.
        :return:
        """
        self.env_dir = Path(ENVIRONMENTS_DIR)
        self.pkg_dir = Path(PACKAGES_DIR)
        self.solver = DependencySolver()

        self.env_dir.mkdir(parents=True, exist_ok=True)
        self.pkg_dir.mkdir(parents=True, exist_ok=True)

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

    def list_packages(self) -> Dict[str, List[str]]:
        """
        List all package specs in PACKAGES_DIR.
        :return:
        """
        result: Dict[str, List[str]] = {}
        for pkg_path in self.pkg_dir.iterdir():
            if not pkg_path.is_dir():
                continue
            name = pkg_path.name
            versions = []
            for ver_path in pkg_path.iterdir():
                if not ver_path.is_dir():
                    continue
                try:
                    # Validate version string
                    _ = Version(ver_path.name)
                    versions.append(ver_path.name)
                except InvalidVersion:
                    logger.warning(f"Ignoring invalid version '{ver_path.name}' for package '{name}'")
            # Sort descending semantic versions
            versions.sort(key=lambda v: Version(v), reverse=True)
            result[name] = versions
        return result

    def install_package(self, env_name: str, requirement: str, dry_run: bool = False) -> List[str]:
        """
        Install a package and its dependencies into an environment.
        requirement can be 'name', 'name-version', or 'name>=x,<y'.
        """
        plugin_manager.trigger("pre_create_env", env_name=env_name, requirement=requirement)
        env_file = self.env_dir / f"{env_name}.yaml"

        if not env_file.exists():
            msg = f"Environment '{env_name}' not found."
            logger.error(msg)
            raise DependencyError(msg)

        env_data = load_yaml(env_file)
        current = set(env_data.get("packages", []))

        try:
            resolved = self.solver.resolve_all([requirement])
        except DependencyError as e:
            logger.error(str(e))
            raise

        to_add = [pv for pv in resolved if pv not in current]
        if not to_add:
            logger.info(f"No new packages to install for requirements '{requirement}'.")
            return []

        if dry_run:
            logger.title(f"[Dry-Run] Would install into '{env_name}':")
            for pkg in to_add:
                logger.info(f"    + {pkg}")
            return to_add

        # Actually save
        env_data["packages"] = sorted(current.union(to_add))
        save_yaml(env_file, env_data)
        logger.success(f"Installed into '{env_name}': {', '.join(to_add)}")

        plugin_manager.trigger("post_create_env", env_name=env_name, requirement=requirement)
        return to_add

    def uninstall_package(self, env_name: str, pkgver: str) -> List[str]:
        """
        Remove a specific package-version from an environment
        :param env_name:
        :param pkgver:
        :return:
        """
        env_file = self.env_dir / f"{env_name}.yaml"
        if not env_file.exists():
            logger.error(f"Environment '{env_name}' not found.")
            return []

        env_data = load_yaml(env_file)
        current = set(env_data.get("packages", []))
        if pkgver not in current:
            logger.warning(f"Package '{pkgver}' is not installed in '{env_name}'.")
            return []

        current.remove(pkgver)
        env_data["packages"] = current
        save_yaml(env_file, env_data)
        logger.success(f"Uninstalled package '{pkgver}' from environment '{env_name}'.")
        return [pkgver]

    def resolve_package_env_vars(self, package_list: List[str]) -> Dict[str, str]:
        """
        Aggregate all 'env' blocks from each package version into a single dict
        """
        merged: Dict[str, str] = {}
        for pv in package_list:
            try:
                name, ver = pv.rsplit('-', 1)
            except ValueError:
                logger.warning(f"Skipping malformed package entry '{pv}'")
                continue

            pkg_file = self.pkg_dir / name / ver / "package.yaml"
            if not pkg_file.exists():
                logger.warning(f"Metadata not found for '{pv}', skipping env-vars.")
                continue

            meta = load_yaml(pkg_file)
            for key, val in meta.get("env", {}).items():
                # Expand placeholders: {root} -> package root path, {PATH} -> existing path
                root = str(self.pkg_dir / name / ver)
                template = val.replace("{root}", root)
                # Support appending to existing variables
                existing = merged.get(key, os.environ.get(key, ""))
                merged[key] = template.replace("{PATH}", existing) if "{PATH}" in template else \
                    f"{template}{os.pathsep if existing else ""}{existing}"
        return merged

    def wrap_tool(
            self,
            source_path: str,
            name: str = None,
            version: str = "0.1.0"
    ) -> str:
        """
        Wrap an existing tool folder into a Nexon package.
        - Copies `source_path` -> ~/.nexon/packages/<name>/<version>/src/
        - Generates a basic package.yaml
        Returns the full package-version string (e.g. "mytool-0.1.0").
        """
        src = Path(source_path).expanduser().resolve()
        if not src.exists() or not src.is_dir():
            raise ValueError(f"Source path invalid or not a directory: {src}")

        # Infer package name if not provided
        pkg_name = name or src.name
        # Validate version
        try:
            Version(version)
        except InvalidVersion:
            raise ValueError(f"Invalid version: {version}")

        pkg_root = Path(PACKAGES_DIR) / pkg_name / version
        pkg_src = pkg_root / "src"
        pkg_root.mkdir(parents=True, exist_ok=True)
        # Ensure clean slate
        if pkg_root.exists():
            logger.warning(f"Overwriting existing package '{pkg_name}-{version}'")
            shutil.rmtree(pkg_root)
        pkg_src.mkdir(parents=True, exist_ok=True)

        # Copy user tool into src/
        shutil.copytree(src, pkg_src, dirs_exist_ok=True)

        # Generate package.yaml
        pkg_file = pkg_root / "package.yaml"
        spec = {
            "name": pkg_name,
            "version": version,
            "description": f"Wrapped tool from {src!s}",
            "requires": [],
            "env": {
                # Expose bin/ and src/ on PATH and PYTHONPATH
                "PATH": "{root}/bin:{PATH}",
                "PYTHONPATH": "{root}/src:{PYTHONPATH}"
            },
            "build": {},
            "commands": {}
        }

        # Helper to register commands
        def register_cmd(path: Path, relative_to: Path):
            """Add all executables in 'path' (not recursive) under commands."""
            for fn in path.iterdir():
                if not fn.is_file():
                    continue
                # on POSIX: check exec bit; on Windows: check known extensions
                is_exec = fn.stat().st_mode & 0o111
                ext = fn.suffix.lower()
                if is_exec or ext in (".sh", ".exe", ".bat", ".py"):
                    cmd_key = fn.stem
                    rel = fn.relative_to(pkg_root)
                    spec["commands"][cmd_key] = (f"{ { 'root': str(pkg_root) } }/{rel.as_posix()}"
                                                 .replace("{root}", str(pkg_root)))

        # If the tool has a `bin/` folder, expose any executable scripts
        bin_dir = pkg_src / "bin"
        if bin_dir.is_dir():
            register_cmd(bin_dir, pkg_src)

        # 2) always scan top-level src/
        register_cmd(pkg_src, pkg_src)

        pkg_file = pkg_root / "package.yaml"
        save_yaml(pkg_file, spec)
        logger.success(f"Wrapped tool as package: {pkg_name}-{version}")
        return f"{pkg_name}-{version}"
