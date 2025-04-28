import typer
from nexon_cli.core.package_manager import list_available_packages


def list_packages():
    """
    List all available packages.
    :return:
    """
    list_available_packages()
