import typer
from nexon_cli.core.env_manager import EnvironmentManager


def deactivate_env():
    """
    Activate an environment
    :return:
    """
    em = EnvironmentManager()
    em.deactivate_environment()
