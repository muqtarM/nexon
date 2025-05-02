import typer
from nexon_cli.core.package_manager import PackageManager


def install_package(
        env_name: str = typer.Argument(..., help="Environment to modify"),
        requirement: str = typer.Argument(..., help="Package or range (e.g. mypkg>=1.2,<2.0"),
        dry_run: bool = typer.Option(False, "--dry-run", "-n",
                                     help="Show what would be installed without changing the environment")
):
    """
    Install a package (and its deps) into an environment
    """
    pm = PackageManager()
    try:
        added = pm.install_package(env_name, requirement, dry_run=dry_run)
    except Exception as e:
        typer.secho(f"Error installing {requirement} -> {e}", fg="red")
        raise typer.Exit(1)

    if not added:
        return

    if dry_run:
        typer.secho("Dry-run complete --- no changes made.", fg="yellow")
    else:
        typer.secho("Installation complete.", fg="green")
