import typer
from nexon_cli.core.workspace_manager import create_workspace


def workspace_create(workspace_name: str):
    """
    Create a new workspace to link multiple environments
    :return:
    """
    create_workspace(workspace_name)
