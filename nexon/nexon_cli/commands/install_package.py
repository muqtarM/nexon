import typer
from nexon_cli.core.package_manager import install_package_to_env


def install_package(env_name: str, package_name: str):
    """
    Install a package into an environment
    :param env_name:
    :param package_name
    :return:
    """
    install_package_to_env(env_name, package_name)
