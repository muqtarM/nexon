import subprocess
from pathlib import Path
from typing import List, Dict

from nexon_cli.utils.file_ops import load_yaml
from nexon_cli.utils.logger import logger
from nexon_cli.utils.shell_ops import set_environment_variables, reset_environment_variables
from nexon_cli.utils.paths import PACKAGES_DIR


class BuildError(Exception):
    """Raised when a package build fails."""


class BuildManager:
    """
    Builds Nexon packages according to their 'build' section in package.yaml.
    Supports any command-line build system (CMake, Makefile, pip, custom scripts).
    """
    def __init__(self):
        self.pkg_dir: Path = Path(PACKAGES_DIR)

        self.pkg_dir.mkdir(parents=True, exist_ok=True)

    def build_package(self, name: str, version: str) -> None:
        """
        Build a package (e.g., C++ plugin via CMake/SCons) based on its build definition.
        """
        pkg_root = self.pkg_dir / name / version
        pkg_file = pkg_root / "package.yaml"
        if not pkg_file.exists():
            msg = f"Package spec not found: {name}-{version}"
            logger.error(msg)
            raise BuildError(msg)

        meta = load_yaml(pkg_file)
        build_cfg: Dict = meta.get("build") or {}

        # Prepare built-time environment variables
        env_overrides = build_cfg.get("env", {})
        # Substitute {root} in env values
        resolved_env = {
            key: val.replace("{root}", str(pkg_root))
            for key, val in env_overrides.items()
        }
        set_environment_variables(resolved_env)

        # Determine commands
        commands: List[str] = build_cfg.get("commands", [])
        if not commands:
            logger.error(f"No build commands defined for '{name}-{version}'. Skipping build")
            reset_environment_variables()
            return

        logger.title(f"Building package: {name}-{version}")
        try:
            for cmd in commands:
                # Substitute {root} placeholder in each command
                cmd_str = cmd.replace("{root}", str(pkg_root))
                logger.info(f"-> {cmd_str}")
                # Run the command in shell; capture output
                completed = subprocess.run(cmd_str, shell=True)
                if completed.returncode != 0:
                    msg = f"Command failed (exit {completed.returncode}): {cmd_str}"
                    logger.error(msg)
                    raise BuildError(msg)
            logger.success(f"Built package: {name}-{version}")
        finally:
            # Always reset environment, even on error
            reset_environment_variables()
