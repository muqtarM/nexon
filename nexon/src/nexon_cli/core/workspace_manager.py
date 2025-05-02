from pathlib import Path
from nexon_cli.utils.file_ops import save_yaml, load_yaml
from nexon_cli.utils.logger import logger
from nexon_cli.utils.paths import WORKSPACES_DIR


def ensure_dirs():
    """
    Ensure the base workspaces directory exists.
    :return:
    """
    WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)


def create_workspace(workspace_name: str):
    """
    Create a new workspace for grouping multiple environments.
    :param workspace_name:
    :return:
    """
    ensure_dirs()
    ws_file = WORKSPACES_DIR / f"{workspace_name}.yaml"
    if ws_file.exists():
        logger.warning(f"Workspace '{workspace_name}' already exists. Overwriting...")

    ws_data = {
        "name": workspace_name,
        "environments": []
    }
    save_yaml(ws_file, ws_data)
    logger.success(f"Workspace '{workspace_name}' created at {ws_file}")


def link_environment_to_workspace(workspace_name: str, env_name: str):
    """
    Link an environment into an existing workspace.
    :param workspace_name:
    :param env_name:
    :return:
    """
    ensure_dirs()
    ws_file = WORKSPACES_DIR / f"{workspace_name}.yaml"
    if not ws_file.exists():
        logger.error(f"Workspace '{workspace_name}' not found.")
        return

    ws_data = load_yaml(ws_file)
    envs = ws_data.get("environments", [])
    if env_name in envs:
        logger.warning(f"Environment '{env_name}' already linked to workspace '{workspace_name}'.")
        return

    envs.append(env_name)
    ws_data["environments"] = envs
    save_yaml(ws_file, ws_data)
    logger.success(f"Environment '{env_name}' linked to workspace '{workspace_name}'.")


def list_workspace_envs(workspace_name: str):
    """
    List all environments linked in a given workspace.
    :param workspace_name:
    :return:
    """
    ws_file = WORKSPACES_DIR / f"{workspace_name}.yaml"
    if not ws_file.exists():
        logger.error(f"Workspace '{workspace_name}' not found.")
        return

    ws_data = load_yaml(ws_file)
    envs = ws_data.get("environments", [])
    if not envs:
        logger.warning(f"No environments linked in workspace '{workspace_name}'.")
        return

    logger.title(f"Environments in Workspace '{workspace_name}'")
    for env in envs:
        logger.info(f"- {env}")
