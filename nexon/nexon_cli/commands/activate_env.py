import typer
from nexon_cli.core.env_manager import activate_environment


def activate_env(env_name: str):
    """
    Activate an environment
    :param env_name:
    :return:
    """
    activate_environment(env_name)
