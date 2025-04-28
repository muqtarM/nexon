import typer
from nexon_cli.core.env_manager import create_environment


def create_env(env_name: str, role: str = typer.Option(None, help="Role template(e.g., animator, game-dev, vp)")):
    """
    Create a new environment.
    :param env_name:
    :param role:
    :return:
    """
    create_environment(env_name, role)
