import typer
from nexon_cli.core.workspace_manager import list_workspace_envs


def workspace_list(workspace_name: str):
    """
    List environments linked to a workspace
    :return:
    """
    list_workspace_envs(workspace_name)
