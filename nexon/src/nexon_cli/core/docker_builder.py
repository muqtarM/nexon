import subprocess
import tempfile
import shutil
from pathlib import Path

from nexon_cli.utils.paths import DOCKERFILES_DIR, ENVIRONMENTS_DIR, PACKAGES_DIR
from nexon_cli.utils.logger import logger


class DockerBuildError(Exception):
    """Raised when a Docker build fails."""


def build_docker_image(env_name: str, tag: str = None) -> str:
    """
    Build a Docker image for a given Nexon environment.
    - Copies all Nexon packages and the environment spec into the build context
    - Installs Nexon via pip
    - Activates the environment inside the container so all deps are installed
    Returns the resulting image tag.
    """
    pkg_dir = Path(PACKAGES_DIR)
    env_dir = Path(ENVIRONMENTS_DIR)
    env_file = env_dir / f"{env_name}.yaml"

    if not env_file.exists():
        msg = f"Environment '{env_name}' not found at {env_file}"
        logger.error(msg)
        raise DockerBuildError(msg)

    # Default image tag if none provided
    if not tag:
        tag = f"nexon/{env_name}:latest"

    logger.title(f"Building Docker image '{tag}' for environment '{env_name}'")

    try:
        with tempfile.TemporaryDirectory() as tmp:
            ctx = Path(tmp)

            # Copy the entire packages directory
            pkg_ctx = ctx / "packages"
            shutil.copytree(pkg_dir, pkg_ctx)

            # Copy only the one environment spec
            env_ctx = ctx / "environments"
            env_ctx.mkdir()
            shutil.copy(env_file, env_ctx / f"{env_name}.yaml")

            # Write Dockerfile
            dockerfile = ctx / "Dockerfile"
            dockerfile.write_text(f"""
FROM python:3.12-slim

# Install NEXON CLI
RUN pip install nexon

# Copy Nexon data
COPY packages /root/.nexon/packages
COPY environments /root/.nexon/environments

# Activate the environment to install its dependencies
RUN nexon activate-env {env_name}

# Default to an interactive shell
CMD ["bash"]
""".strip())

            # Build the Docker image
            cmd = ["docker", "build", "-t", tag, str(ctx)]
            logger.info(f"Running: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        msg = f"Docker build failed (exit code {e.returncode})"
        logger.error(msg)
        raise DockerBuildError(msg)
    except Exception as e:
        msg = f"Docker build error: {e}"
        logger.error(msg)
        raise DockerBuildError(msg)

    logger.success(f"Docker image build successfully: {tag}")
    return tag
