import importlib
import yaml
from pathlib import Path
from typing import Dict, List, Callable

from nexon_cli.core.configs import config
from nexon_cli.utils.logger import logger

HOOK_POINTS = [
    "pre_create_env",
    "post_create_env",
    "pre_install_package",
    "post_install_package",
    "pre_build_package",
    "post_build_package",
    "pre_activate_env",
    "post_activate_env",
    # ...add more as needed...
]


class PluginManager:
    def __init__(self):
        self.plugins_dir = Path(config.base_dir) / "plugins"
        self.plugins_file = Path(config.base_dir) / "plugins.yaml"
        self._hooks: Dict[str, List[Callable]] = {h: [] for h in HOOK_POINTS}
        self._load_enabled_plugins()

    def _load_enabled_plugins(self):
        if not self.plugins_file.exists():
            logger.info("No plugins.yaml found - skipping plugin load.")
            return
        data = yaml.safe_load(open(self.plugins_file)) or {}
        for name in data.get("plugins", []):
            try:
                mod_path = f"nexon_cli.plugins.{name}.hooks"
                module = importlib.import_module(mod_path)
                for hook_name in HOOK_POINTS:
                    fn = getattr(module, hook_name, None)
                    if callable(fn):
                        self._hooks[hook_name].append(fn)
                        logger.info(f"Registered hook {hook_name} from plugin {name}")
            except ImportError as e:
                logger.error(f"Failed to load plugin '{name}': {e}")

    def trigger(self, hook: str, **kwargs):
        """
        Call all registered hook functions for the given hook point,
        passing kwargs through.
        """
        for fn in self._hooks.get(hook, []):
            try:
                fn(**kwargs)
            except Exception as e:
                logger.error(f"Plugin hook error in {fn.__module__}.{fn.__name__}: {e}")


# expose a singleton
plugin_manager = PluginManager()
