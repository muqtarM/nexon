from pathlib import Path
import getpass
import yaml

from nexon_cli.core.configs import config
from nexon_cli.utils.logger import logger


class LayerError(Exception):
    pass


class LayerManager:
    """
    Handles loading and merging of environment layers:
    global -> team -> project -> user -> env.
    """

    def __init__(self):
        # ensure base dirs
        config.layers_dir.mkdir(exist_ok=True, parents=True)
        for sub in ("team", "project", "user"):
            (getattr(config, f"{sub}_layers")).mkdir(exist_ok=True, parents=True)

    def _load_yaml(self, path: Path) -> dict:
        if not path.exists():
            return {}
        with open(path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}

    def get_effective(self,
                      env_name: str,
                      team: str,
                      project: str,
                      user: str = None) -> dict:
        """
        Returns a merged dict of:
            global + team/team.yaml + project/project.yaml + user/user.yaml + environments/env_name.yaml
        """
        merged = {}
        # 1) global
        merged.update(self._load_yaml(config.global_layer))
        # 2) team
        merged.update(self._load_yaml(config.team_layers / f"{team}.yaml"))
        # 3) project
        merged.update(self._load_yaml(config.project_layers / f"{project}.yaml"))
        # 4) user
        user = user or getpass.getuser()
        merged.update(self._load_yaml(config.user_layers / f"{user}.yaml"))
        # 5) the environment itself
        env_file = Path(config.environments_dir) / f"{env_name}.yaml"
        if not env_file.exists():
            raise LayerError(f"Environment '{env_name}' not found.")
        merged.update(self._load_yaml(env_file))
        return merged

    def create_layer(self, level: str, name: str, data: dict):
        """
        Create or overwrite a layer yaml at given level: global|team|project|user.
        """
        if level == "global":
            path = config.global_layer
        elif level in ("team", "project", "user"):
            path = getattr(config, f"{level}_layers") / f"{name}.yaml"
        else:
            raise LayerError(f"Unknown layer level: {level}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f)
        logger.success(f"Written {level} layer: {path}")

    def list_layers(self) -> dict:
        """
        Returns a mapping of level -> list of layer names.
        """
        out = {
            "global":       ["global"] if config.global_layer.exists() else [],
            "team":         [p.stem for p in config.team_layers.glob("*.yaml")],
            "project":      [p.stem for p in config.project_layers.glob("*.yaml")],
            "user":         [p.stem for p in config.user_layers.glob("*.yaml")]
        }
        return out


# and expose singleton
layer_manager = LayerManager()
