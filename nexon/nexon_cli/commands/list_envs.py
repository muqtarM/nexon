import typer
from nexon_cli.core.env_manager import list_environments


def list_envs():
    """
    List all available environments.
    :return:
    """
    list_environments()
