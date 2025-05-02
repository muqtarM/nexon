import typer
from nexon_cli.core.package_manager import PackageManager


def list_packages():
    """
    List all available packages.
    :return:
    """
    pm = PackageManager()
    packages = pm.list_packages()
    if not packages:
        typer.echo(f"[yellow]No packages found[/yellow]")
        return
    for name, vers in packages.items():
        typer.secho(f"    + {name}", fg="green")
        for v in vers:
            typer.secho(f"        + {v}", fg="green")
        typer.secho()
