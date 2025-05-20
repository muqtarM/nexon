import sys
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional

from nexon_cli.utils.logger import logger
from nexon_cli.utils.file_ops import save_yaml, load_yaml
from nexon_cli.utils.shell_ops import set_environment_variables, reset_environment_variables
from nexon_cli.core.interpreter_manager import InterpreterManager
from nexon_cli.core.auth_manager import AuthManager, AuthError
from nexon_cli.models.environment_model import EnvironmentModel
from nexon_cli.core.package_manager import PackageManager
from nexon_cli.core.plugin_manager import plugin_manager
from nexon_cli.core.configs import config
from nexon_cli.utils.audit import log


# Main Environment Manager
class EnvironmentManager:
    def __init__(self):
        self.auth = AuthManager()
        self.interpreter_manager = InterpreterManager()
        # Ensure base directory exists
        self.envs_dir = Path(config.environments_dir)
        self.envs_dir.mkdir(parents=True, exist_ok=True)

    def create_environment(self, env_name: str, role: str = None):
        """
        Create a new environment YAML based on the role template
        :param env_name:
        :param role:
        :return:
        """
        # Check permission
        self.auth.check("create_env")

        plugin_manager.trigger("pre_create_env", env_name=env_name, role=role)

        env_path = self.envs_dir / f"{env_name}.yaml"

        if env_path.exists():
            logger.warning(f"Environment '{env_name}' already exists. Overwriting...")

        env_data = EnvironmentModel(
            name=env_name,
            created_at=datetime.utcnow().isoformat(),
            description=f"Environment created via Nexon CLI [{role}]" if role else "Custom environment",
            role=role or "custom",
            packages=[],  # User will install packages later
        )

        save_yaml(env_path, env_data.model_dump())
        logger.success(f"Environment '{env_name}' created successfully!")

        # Audit log it
        log("create_env", self.auth.current_user(), env_name, details=f"role={role}")

        plugin_manager.trigger("post_create_env", env_name=env_name, role=role)

    def activate_environment(self, env_name: str):
        """
        Activate the environment by setting up required variables.
        :param env_name:
        :return:
        """
        # No strict permission needed for activation
        self.auth.check("activate_env")  # You can allow all to activate

        env_file = self.envs_dir / f"{env_name}.yaml"
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
        }

        pm = PackageManager()

        # Resolve PYTHONPATH and other variables from installed packages
        resolved_vars = pm.resolve_package_env_vars(package_list)
        env_vars.update(resolved_vars)

        # Apply the environment variables to the current shell session
        set_environment_variables(env_vars)

        logger.success(f"Environment '{env_name}' activated successfully!")
        logger.info(f"Packages Loaded: {', '.join(package_list) if package_list else 'None'}")
        logger.info(f"Python Interpreter: {interpreter_path}")

        # Audit log
        log("activate_env", self.auth.current_user(), env_name)

    def deactivate_environment(self):
        """
        Deactivate the currently active environment
        :return:
        """
        reset_environment_variables()
        logger.info("Environment variables reset to system defaults.")

    def list_environments(self, return_data: bool = False) -> List[Dict[str, Any]] | None:
        """
        If return_data is False: print env names to console (old behaviour).
        If return_data is True: return a list of dicts with keys:
            - name: str
            - role: str
            - created_at: str
        """
        all_files = sorted(self.envs_dir.glob("*.yaml"))
        # Filter our lockfiles
        env_files = [f for f in all_files if not f.name.endswith(".lock.yaml")]

        if return_data:
            result = []
            for f in env_files:
                data = load_yaml(f)
                result.append({
                    "name": data.get("name", f.stem),
                    "role": data.get("role", "custom"),
                    "created_at": data.get("created_at", "")
                })
            return result

        # Old CLI behavior
        if not env_files:
            logger.warning("No environments found.")
            return

        logger.title("Available Environments")
        for f in env_files:
            logger.info(f"- {f.stem}")

    def get_environment(self, env_name: str) -> Dict[str, Any]:
        """
        Load and return the full YAML for the named environment.
        Raises FileNotFoundError if missing.
        """
        env_file = self.envs_dir / f"{env_name}.yaml"
        if not env_file.exists():
            raise FileNotFoundError(f"Environment '{env_name}' not found.")
        return load_yaml(env_file)

    def lock_environment(self, env_name: str):
        """
        Create a lockfile (nexon.lock.yaml) for reproducibility
        :param env_name:
        :return:
        """

        env_file = self.envs_dir / f"{env_name}.yaml"
        if not env_file.exists():
            logger.error(f"Environment '{env_name}' does not exist.")
            return

        env_data = load_yaml(env_file)
        lockfile_path = self.envs_dir / f"{env_name}.lock.yaml"

        save_yaml(lockfile_path, env_data)
        logger.success(f"Lockfile created: {lockfile_path}")

    def diff_environments(self, env_a: str, env_b: str) -> None:
        """
        Print the differences in packages and role between two environments.
        :param env_a:
        :param env_b:
        :return:
        """
        file_a = self.envs_dir / f"{env_a}.yaml"
        file_b = self.envs_dir / f"{env_b}.yaml"

        if not file_a.exists():
            logger.error(f"Environment '{env_a}' not found at {file_a}")
            return
        if not file_b.exists():
            logger.error(f"Environment '{env_b}' not found at {file_b}")
            return

        data_a = load_yaml(file_a)
        data_b = load_yaml(file_b)

        pkgs_a = set(data_a.get("packages", []))
        pkgs_b = set(data_b.get("packages", []))

        added = pkgs_b - pkgs_a
        removed = pkgs_a - pkgs_b

        logger.title(f"Diff: {env_a} -> {env_b}")

        if added:
            logger.success("Packages Added:")
            for pkg in sorted(added):
                logger.success(f"    + {pkg}")
        else:
            logger.info("No packages added.")

        if removed:
            logger.warning("Packages Removed:")
            for pkg in sorted(removed):
                logger.warning(f"    - {pkg}")
        else:
            logger.info("No packages removed.")

        role_a = data_a.get("role", "custom")
        role_b = data_b.get("role", "custom")
        if role_a != role_b:
            logger.info(f"Role changed: {role_a} -> {role_b}")
        else:
            logger.info(f"Role unchanged: {role_a }")

    def export_env_file(self, env_name: str, output_path: Optional[str] = None) -> str:
        """
        Export the activation environment variables for `env_name` into a dotenv file.
        If `output_path` is provided, writes to the file; otherwise returns the content.
        """
        # Ensure environment exists and load base data
        env_file = self.envs_dir / f"{env_name}.yaml"
        if not env_file.exists():
            raise FileNotFoundError(f"Environment '{env_name}' not found.")

        # Merge package env-vars
        data = load_yaml(env_file)
        pkg_vars = []
        # Compose package_env_vars
        pm = PackageManager()
        pkg_list = data.get("packages", [])
        pkg_vars_dict = pm.resolve_package_env_vars(pkg_list)

        # Also include NEXON_ENV
        pkg_vars_dict["NEXON_ENV"] = env_name

        # Generate dotenv content
        lines = []
        for key, val in pkg_vars_dict.items():
            # quote values containing spaces or path separators
            if " " in val:
                val = f'"{val}"'
            lines.append(f"{key}={val}")

        content = "\n".join(lines) + "\n"

        if output_path:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(content)
            return output_path
        else:
            return content
