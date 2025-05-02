import subprocess
from pathlib import Path
from typing import Optional

from nexon_cli.utils.paths import *
from nexon_cli.utils.logger import logger
from nexon_cli.core.docker_builder import build_docker_image, DockerBuildError


class RenderError(Exception):
    """Raised when render farm submission fails"""


class RenderManager:
    """
    Handles render farm and CI job submission for Nexon environments.
    """

    def __init__(self):
        self.env_dir = Path(ENVIRONMENTS_DIR)
        self.render_farm_cli = "deadlinecommand"  # Example farm CLI
        self.ci_cli = "gh"  # Example GitHub CLI for CI

    def submit_render(
            self,
            env_name: str,
            scene_file: str,
            farm: str = "deadline",
            options: Optional[str] = None
    ) -> str:
        """
        Submit a render job to the specified farm.
        """
        env_file = self.env_dir / f"{env_name}.yaml"
        if not env_file.exists():
            raise RenderError(f"Environment '{env_name}' not found")

        # Build Docker image for isolated render
        tag = f"nexon/{env_name}:render"
        try:
            image = build_docker_image(env_name, tag)
        except DockerBuildError as e:
            raise RenderError(f"Docker build failed: {e}")

        # Construct render submission command
        cmd = [
            self.render_farm_cli,
            "SubmitRenderJob",
            "-Priority", "50",
            "-Image", image,
            "-SceneFile", scene_file
        ]
        if options:
            cmd += options.split()

        logger.info(f"Submitting render job: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise RenderError(f"Render submission failed: {e}")
        return f"Submitted render job for scene '{scene_file}' on farm '{farm}'"

    def run_cli(
            self,
            env_name: str,
            script: str,
            runner: str = "github-actions"
    ) -> str:
        """
        Trigger a CI workflow using the specified runner.
        """
        # Build Docker image tag
        tag = f"nexon/{env_name}:ci"
        try:
            build_docker_image(env_name, tag)
        except DockerBuildError as e:
            raise RenderError(f"Docker build failed: {e}")

        # Construct CI trigger command
        cmd = [
            self.ci_cli,
            "workflow", "run",
            f"{runner}.yaml",
            "--ref", "main",
            "--field", f"env={env_name}",
            "--field", f"script={script}"
        ]

        logger.info(f"Triggering CI workflow: {' '.join(cmd)}")
        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise RenderError(f"Ci workflow trigger failed: {e}")
        return f"Triggered CI workflow '{runner}' for env '{env_name}'"


# Expose a singleton
render_manager = RenderManager()
