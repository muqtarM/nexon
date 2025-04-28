import typer
from nexon_cli.core.build_manager import build_package


def build_package_cmd(package_name: str):
    """
    Build a package (e.g., C++ plugin via CMake, Makefile, or SCons).
    :param package_name:
    :return:
    """
    build_package(package_name)
