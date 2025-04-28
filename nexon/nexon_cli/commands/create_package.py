import typer
from nexon_cli.core.package_manager import create_package


def create_package_cmd(package_name: str):
    """
    Create a new custom package template.
    :param package_name:
    :return:
    """
    create_package(package_name)
