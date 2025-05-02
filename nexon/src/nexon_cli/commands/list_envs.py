import typer
from nexon_cli.core.env_manager import EnvironmentManager


def list_envs():
    """
    List all available environments.
    :return:
    """
    em = EnvironmentManager()
    em.list_environments()
