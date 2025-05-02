import typer
from nexon_cli.core.package_manager import PackageManager


def list_packages():
    """
    List all available packages.
    :return:
    """
    pm = PackageManager()
    pm.list_packages()
