import typer
from nexon_cli.core.package_manager import PackageManager


def create_package_cmd(package_name: str, version: str = typer.Option("0.1.0", help="Initial package version")):
    """
    Create a new custom package template.
    :param package_name:
    :param version
    :return:
    """
    pm = PackageManager()
    try:
        pm.create_package(package_name, version)
        typer.secho(f"Package scaffolded: {package_name}-{version}", fg="green")
    except Exception as e:
        typer.secho(f"Error creating package: {e}", fg="red")
        raise typer.Exit(1)
