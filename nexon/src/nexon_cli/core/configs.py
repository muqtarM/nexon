# nexon_cli/core/config.py
import os
from pathlib import Path


class NexonConfig:
    """
    Centralized configuration for Nexon directories and layers.
    Ensures all required directories exist under the base_dir.
    """
    def __init__(self):
        # Base directory for all Nexon data
        self.base_dir: Path = Path(os.getenv("NEXON_BASE_DIR", Path.home() / ".nexon"))
        self._ensure_directory(self.base_dir)

        # Ensure core subdirectories
        for subdir in (
            self.environments_dir,
            self.packages_dir,
            self.workspaces_dir,
            self.recipes_dir,
            self.dockerfiles_dir,
            self.layers_dir,
            self.team_layers,
            self.project_layers,
            self.user_layers,
        ):
            self._ensure_directory(subdir)

    def _ensure_directory(self, path: Path):
        """
        Create the directory if it does not exist.
        """
        path.mkdir(parents=True, exist_ok=True)

    @property
    def environments_dir(self) -> Path:
        """Directory where environment specs (*.yaml) are stored."""
        return self.base_dir / "environments"

    @property
    def packages_dir(self) -> Path:
        """Directory where package folders are stored."""
        return self.base_dir / "packages"

    @property
    def workspaces_dir(self) -> Path:
        """Directory for workspace groupings."""
        return self.base_dir / "workspaces"

    @property
    def recipes_dir(self) -> Path:
        """Directory for recipe definitions."""
        return self.base_dir / "recipes"

    @property
    def dockerfiles_dir(self) -> Path:
        """Directory for generated Dockerfiles, if used."""
        return self.base_dir / "dockerfiles"

    @property
    def layers_dir(self) -> Path:
        """Root directory for configuration layers (global, team, project, user)."""
        return self.base_dir / "layers"

    @property
    def global_layer(self) -> Path:
        """Path to the global layer YAML (global defaults)."""
        return self.layers_dir / "global.yaml"

    @property
    def team_layers(self) -> Path:
        """Directory containing per-team layer YAMLs."""
        return self.layers_dir / "team"

    @property
    def project_layers(self) -> Path:
        """Directory containing per-project layer YAMLs."""
        return self.layers_dir / "project"

    @property
    def user_layers(self) -> Path:
        """Directory containing per-user layer YAMLs."""
        return self.layers_dir / "user"

    @property
    def shotgrid_url(self) -> str | None:
        return os.environ.get("SHOTGRID_URL")

    @property
    def shotgrid_script(self) -> str | None:
        return os.environ.get("SHOTGRID_SCRIPT")

    @property
    def shotgrid_key(self) -> str | None:
        return os.environ.get("SHOTGRID_KEY")

    @property
    def p4_port(self) -> str | None:
        return os.environ.get("P4_PORT")

    @property
    def p4_user(self) -> str | None:
        return os.environ.get("P4_USER")

    @property
    def p4_client(self) -> str | None:
        return os.environ.get("P4_CLIENT")

    @property
    def telemetry_url(self) -> str | None:
        return os.environ.get("TELEMETRY_URL")

    @property
    def telemetry_api_key(self) -> str | None:
        return os.environ.get("TELEMETRY_API_KEY")

    @property
    def telemetry_enabled(self) -> bool:
        return os.environ.get("TELEMETRY_ENABLED", False)

    @property
    def server_url(self) -> str:
        return os.environ.get("NEXON_SERVER_URL", "")

    @property
    def cli_token(self) -> str:
        return os.environ.get("NEXON_CLI_TOKEN", "")


# Singleton instance for import across Nexon modules
config = NexonConfig()
