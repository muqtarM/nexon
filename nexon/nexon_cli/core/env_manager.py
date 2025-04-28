import os
import sys
from pathlib import Path
from datetime import datetime
import yaml

from nexon_cli.utils.logger import logger
from nexon_cli.utils.file_ops import save_yaml, load_yaml
from nexon_cli.utils.shell_ops import set_environment_variables, reset_environment_variables
from nexon_cli.core.interpreter_manager import InterpreterManager
from nexon_cli.models.environment_model import EnvironmentModel

ENVIRONMENTS_DIR = Path.home() / ".nexon" / "environments"


# Main Environment Manager
class EnvironmantManager:
    def __init__(self):
        self.interpreter_manager = InterpreterManager()

    def create_environment(self, env_name: str, role: str = None):
        """
        Create a new environment YAML based on the role template
        :param env_name:
        :param role:
        :return:
        """
        env_path = ENVIRONMENTS_DIR / f"{env_name}.yaml"
        os.makedirs(ENVIRONMENTS_DIR, exist_ok=True)

        if env_path.exists():
            logger.warning(f"Environment '{env_name}' already exists. Overwriting...")

        env_data = EnvironmentModel(
            name=env_name,
            created_at=datetime.utcnow().isoformat(),
            description=f"Environment created via Nexon CLI [{role}]" if role else "Custom environment",
            role=role or "custom",
            packages=[],  # User will install packages later
        )

        save_yaml(env_path, env_data.dict())
        logger.success(f"Environment '{env_name}' created successfully!")

    def activate_environment(self, env_name: str):
        """
        Activate the environment by setting up required variables.
        :param env_name:
        :return:
        """

        env_file = ENVIRONMENTS_DIR / f"{env_name}.yaml"
        if not env_file.exists():
            logger.error(f"Environment '{env_name}' does not exist.")
            return

        env_data = load_yaml(env_file)
        package_list = env_data.get("packages", [])

        if not package_list:
            logger.warning(f"No packages defined for environment '{env_name}'. Proceeding without packages.")

        # Resolve the correct Python interpreter
        interpreter_path = self.interpreter_manager.resolve_interpreter(package_list)

        # Infor about Python interpreter being used
        if interpreter_path != sys.executable:
            logger.warning(f"Environment '{env_name}' prefers a different Python interpreter: {interpreter_path}.")
            logger.warning(f"Consider launching DCCs with Nexon launcher for best compatibility.")

        # Build environment variables from package specs (placeholder function for now)
        env_vars = {
            "NEXON_ENV": env_name,
            "PYTHONPATH": "",  # Will be populated below
        }

        # Resolve PYTHONPATH and other variables from installed packages
        resolved_vars = resolve_package_env_vars(package_list)
        env_vars.update(resolved_vars)

        # Apply the environment variables to the current shell session
        set_environment_variables(env_vars)

        logger.success(f"Environment '{env_name}' activated successfully!")
        logger.info(f"Packages Loaded: {', '.join(package_list) if package_list else 'None'}")
        logger.info(f"Python Interpreter: {interpreter_path}")

    def deactivate_environment(self):
        """
        Deactivate the currently active environment
        :return:
        """
        reset_environment_variables()
        logger.info("Environment variables reset to system defaults.")

    def list_environments(self):
        """
        List all available enviroments.
        :return:
        """

        if not ENVIRONMENTS_DIR.exists():
            logger.warning("No environments found.")
            return

        envs = [f.stem for f in ENVIRONMENTS_DIR.glob("*.yaml")]

        if not envs:
            logger.warning("No environments created yet.")
            return

        logger.title("Available Environments")
        for env in envs:
            logger.info(f"- {env}")

    def lock_environment(self, env_name: str):
        """
        Create a lockfile (nexon.lock.yaml) for reproducibility
        :param env_name:
        :return:
        """

        env_file = ENVIRONMENTS_DIR / f"{env_name}.yaml"
        if not env_file.exists():
            logger.error(f"Environment '{env_name}' does not exist.")
            return

        env_data = load_yaml(env_file)
        lockfile_path = ENVIRONMENTS_DIR / f"{env_name}.lock.yaml"

        save_yaml(lockfile_path, env_data)
        logger.success(f"Lockfile created: {lockfile_path}")
