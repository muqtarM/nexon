import typer
from nexon_cli.core.env_manager import EnvironmentManager


def lock_env(env_name: str):
    """
    Generate a lockfile for the environment (for reproducibility).
    :param env_name:
    :return:
    """
    em = EnvironmentManager()
    em.lock_environment(env_name)
