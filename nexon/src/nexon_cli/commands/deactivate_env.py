import typer
from nexon_cli.core.env_manager import EnvironmantManager


def deactivate_env():
    """
    Activate an environment
    :return:
    """
    em = EnvironmantManager()
    em.deactivate_environment()
