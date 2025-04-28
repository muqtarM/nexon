import typer
from nexon_cli.core.package_manager import uninstall_package_to_env


def uninstall_package(env_name: str, package_name: str):
    """
    Remove a package from an environment
    :param env_name:
    :param package_name
    :return:
    """
    uninstall_package_to_env(env_name, package_name)
