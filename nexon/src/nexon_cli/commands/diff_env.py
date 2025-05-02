import typer
from nexon_cli.core.env_manager import EnvironmentManager


def diff_env(
        env_a: str = typer.Argument(..., help="Name of the source environment"),
        env_b: str = typer.Argument(..., help="Name of the target environment")
):
    """
    Show differences between two environments (packages and environment variables).
    :param env_a:
    :param env_b:
    :return:
    """
    em = EnvironmentManager()
    em.diff_environments(env_a, env_b)
