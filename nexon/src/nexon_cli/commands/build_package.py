import typer
from nexon_cli.core.build_manager import build_manager


def build_package_cmd(
        package_name: str,
        version: str = typer.Argument(..., help="Version of the package to build")
):
    """
    Build a specific package version using its build spec.

    Example: nexon build-package mytool 1.2.3
    """
    try:
        build_manager.build_package(package_name, version)
    except Exception as e:
        typer.secho(f"Error building '{package_name}-{version}': {e}", fg="red")
        raise typer.Exit(1)
