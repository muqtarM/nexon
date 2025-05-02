import typer
from nexon_cli.core.package_manager import PackageManager


def uninstall_package(env_name: str, pkgver: str):
    """
    Remove a package from an environment
    :param env_name:
    :param pkgver
    :return:
    """
    pm = PackageManager()
    try:
        pm.uninstall_package(env_name, pkgver)
        typer.echo(f"[green]Removed:[/green] {pkgver}")
    except Exception as e:
        typer.secho(f"Error uninstalling {pkgver} -> {e}", fg="red")
        raise typer.Exit(1)
