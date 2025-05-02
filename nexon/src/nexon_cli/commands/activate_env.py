import typer
from nexon_cli.core.env_manager import EnvironmentManager


def activate_env(env_name: str):
    """
    Activate an environment
    :param env_name:
    :return:
    """
    em = EnvironmentManager()
    em.activate_environment(env_name)
