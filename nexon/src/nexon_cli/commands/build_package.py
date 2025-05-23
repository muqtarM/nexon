import typer
# from nexon_cli.core.build_manager import BuildManager, BuildError
from nexon_cli.core.tasks import build_package_task


# bm = BuildManager()

def build_package_cmd(
        package: str = typer.Argument(..., help="Package name (e.g. mytool)"),
        version: str = typer.Argument(..., help="Package version (e.g. 1.0.0)")
):
    """
    Build a specific package version using its build spec.

    Example: nexon build-package mytool 1.2.3
    """
    result = build_package_task.delay(package, version)
    typer.secho(f"Enqueued build: {result.id}", fg="cyan")
    # try:
    #     bm.build_package(package, version)
    # except BuildError as e:
    #     typer.secho(str(e), fg="red")
    #     raise typer.Exit(1)
    # else:
    #     typer.secho(f"Package built: {package}-{version}", fg="green")
