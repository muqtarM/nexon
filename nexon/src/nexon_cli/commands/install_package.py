import typer
from nexon_cli.core.package_manager import PackageManager


def install_package(env_name: str, requirement: str):
    """
    Install a package into an environment
    :param env_name:
    :param requirement
    :return:
    """
    pm = PackageManager()
    try:
        added = pm.install_package(env_name, requirement)
        if added:
            typer.echo(f"[green]Installed:[/green] {', '.join(added)}")
        else:
            typer.echo(f"[yellow]Nothing to install. Requirement already satisfied:[/yellow] {requirement}")
    except Exception as e:
        typer.secho(f"Error installing {requirement} -> {e}", fg="red")
        raise typer.Exit(1)
