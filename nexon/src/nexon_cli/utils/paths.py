import os
from pathlib import Path

# Base directory for all Nexon data; override via NEXON_HOME env var
BASE_DIR = Path(os.getenv("NEXON_BASE_DIR", Path.home() / ".nexon"))

# Core subdirectories
ENVIRONMENTS_DIR = BASE_DIR / "environments"
PACKAGES_DIR = BASE_DIR / "packages"
WORKSPACES_DIR = BASE_DIR / "workspaces"
RECIPES_DIR = BASE_DIR / "recipes"
SETTINGS_PATH = BASE_DIR / "settings.yaml"
DOCKERFILES_DIR = BASE_DIR / "dockerfiles"

# Ensure all directories exists (call at startup of CLI/core operations)
for d in (ENVIRONMENTS_DIR, PACKAGES_DIR, WORKSPACES_DIR, RECIPES_DIR):
    d.mkdir(parents=True, exist_ok=True)
