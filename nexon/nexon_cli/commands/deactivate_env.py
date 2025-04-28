import typer
from nexon_cli.core.env_manager import deactivate_environment


def deactivate_env():
    """
    Activate an environment
    :return:
    """
    deactivate_environment()
