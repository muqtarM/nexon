# nexon_cli/core/recipe_manager.py

from pathlib import Path
from typing import List

from nexon_cli.utils.paths import RECIPES_DIR, ENVIRONMENTS_DIR
from nexon_cli.utils.file_ops import save_yaml, load_yaml
from nexon_cli.utils.logger import logger


class RecipeManager:
    """
    Manage creation, listing, and application of project-specific recipes.
    """
    def __init__(self):
        self.recipes_dir = RECIPES_DIR
        self.env_dir = ENVIRONMENTS_DIR

    def create_recipe(self, name: str, base_environment: str = "") -> None:
        """
        Scaffold a new recipe: ~/.nexon/recipes/<name>.yaml
        """
        self.recipes_dir.mkdir(parents=True, exist_ok=True)
        rcp_file = self.recipes_dir / f"{name}.yaml"

        if rcp_file.exists():
            logger.warning(f"Recipe '{name}' already exists; overwriting.")

        data = {
            "name": name,
            "base_environment": base_environment,
            "overrides": [],
            "env": {}
        }
        save_yaml(rcp_file, data)
        logger.success(f"Scaffolded recipe: {name}")

    def list_recipes(self) -> List[str]:
        """
        List all available recipe names.
        """
        self.recipes_dir.mkdir(parents=True, exist_ok=True)
        files = sorted(self.recipes_dir.glob("*.yaml"))
        if not files:
            logger.warning("No recipes found.")
            return []

        names: List[str] = []
        logger.title("Available Recipes")
        for f in files:
            data = load_yaml(f)
            name = data.get("name", f.stem)
            base = data.get("base_environment", "<none>")
            logger.info(f"- {name} (base: {base})")
            names.append(name)
        return names

    def apply_recipe(self, name: str) -> None:
        """
        Apply a recipe by merging into its base environment.
        """
        rcp_file = self.recipes_dir / f"{name}.yaml"
        if not rcp_file.exists():
            logger.error(f"Recipe '{name}' not found.")
            return

        data = load_yaml(rcp_file)
        base_env = data.get("base_environment")
        if not base_env:
            logger.error(f"Recipe '{name}' has no base_environment set.")
            return

        env_file = self.env_dir / f"{base_env}.yaml"
        if not env_file.exists():
            logger.error(f"Base environment '{base_env}' not found.")
            return

        env_data = load_yaml(env_file)
        pkgs = env_data.get("packages", [])
        overrides = data.get("overrides", [])
        added_pkgs = [p for p in overrides if p not in pkgs]
        pkgs.extend(added_pkgs)
        env_data["packages"] = pkgs

        extra_env = data.get("env", {})
        if extra_env:
            existing_env = env_data.get("env", {})
            existing_env.update(extra_env)
            env_data["env"] = existing_env

        save_yaml(env_file, env_data)
        logger.success(f"Applied recipe '{name}' to '{base_env}'.")
        if added_pkgs:
            logger.info(f"  Added packages: {', '.join(added_pkgs)}")
        if extra_env:
            logger.info(f"  Added env-vars: {', '.join(extra_env.keys())}")
