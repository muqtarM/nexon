import subprocess
from pathlib import Path
from typing import Optional, List

from nexon_cli.utils.file_ops import load_yaml, save_yaml
from nexon_cli.utils.logger import logger
from nexon_cli.utils.shell_ops import set_environment_variables, reset_environment_variables
from nexon_cli.utils.paths import PACKAGES_DIR, DOCKERFILES_DIR, ENVIRONMENTS_DIR


class BuildManager:
    """
    Handle building of packages (CMake, PEP-517, custom) and Docker images
    """
    def __init__(self):
        self.pkg_dir: Path = PACKAGES_DIR
        self.docker_dir = DOCKERFILES_DIR

    def build_package(self, name: str, version: str) -> None:
        """
        Build a package (e.g., C++ plugin via CMake/SCons) based on its build definition.
        """
        pkg_root = self.pkg_dir / name / version
        pkg_file = pkg_root / "package.yaml"
        if not pkg_file.exists():
            logger.error(f"Package spec not found: {name}-{version}")
            return

        # Load spec
        data = load_yaml(pkg_file)
        build_spec = data.get("build") or {}
        env_vars = data.get("env", {})

        if env_vars:
            set_environment_variables(env_vars)
            logger.info(f"Applied env-vars for build '{name}-{version}'.")

        # Determine commands
        commands: List[str] = build_spec.get("commands", [])
        if not commands:
            logger.error(f"No build commands for '{name}-{version}'. Skipping build")
            reset_environment_variables()
            return

        # Execute each build command sequentially
        for cmd in commands:
            logger.info(f"Building '{name}-{version}': '{cmd}'")
            result = subprocess.call(cmd, shell=True, cwd=str(pkg_root))
            if result != 0:
                logger.error(f"Build failed for '{name}-{version}' (exit {result})")
                reset_environment_variables()
                return

        reset_environment_variables()
        logger.success(f"Package '{name}-{version}' build successfully.")

    def build_docker_image(self, env_name: str, tag: Optional[str] = None) -> None:
        """
        Build a Docker image for a given environment.
        Uses lockfile if available, else env spec.
        """
        env_file = ENVIRONMENTS_DIR / f"{env_name}.yaml"
        lock_file = ENVIRONMENTS_DIR / f"{env_name}.lock.yaml"
        if not env_file.exists():
            logger.error(f"Environment '{env_name}' not found.")
            return

        spec_file = lock_file if lock_file.exists() else env_file
        env_data = load_yaml(spec_file)
        packages = env_data.get("packages", [])

        # Prepare Docker context
        docker_env_dir = self.docker_dir / env_name
        docker_env_dir.mkdir(parents=True, exist_ok=True)
        dockerfile = docker_env_dir / "Dockerfile"

        lines = [
            "FROM python:3.12-slim",
            "WORKDIR /workspace",
            "RUN apt-get update && apt-get install -y git wget build-essential && rm -rf /var/lib/apt/lists/*",
            f"COPY {spec_file.name} /workspace/"
        ]
        # Placeholder for package-specific install
        lines.append("# TODO: Add installation steps for packages: {}".format(', '.join(packages)))

        dockerfile.write_text("\n".join(lines), encoding='utf-8')
        save_yaml(docker_env_dir / spec_file.name, env_data)

        img_tag = tag or f"nexon/{env_name}:latest"
        cmd = ["docker", "build", "-t", img_tag, str(docker_env_dir)]
        logger.info(f"Starting Docker build: {img_tag}")
        result = subprocess.call(cmd)
        if result != 0:
            logger.error(f"Docker build failed (exit {result})")
            return

        logger.success(f"Docker image build: {img_tag}")


# Singleton instance for easy import
build_manager = BuildManager()
