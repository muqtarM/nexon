import typer
from nexon_cli.core.env_manager import EnvironmantManager


def list_envs():
    """
    List all available environments.
    :return:
    """
    em = EnvironmantManager()
    em.list_environments()
