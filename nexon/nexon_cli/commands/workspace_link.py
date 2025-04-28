import typer
from nexon_cli.core.workspace_manager import link_environment_to_workspace


def workspace_link(workspace_name: str, env_name: str):
    """
    Link an existing environment into a workspace.
    :return:
    """
    link_environment_to_workspace(workspace_name, env_name)
