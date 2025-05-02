import typer
from nexon_cli.core.package_manager import PackageManager


def wrap_tool(
        source_path: str = typer.Argument(..., help="Path to your tool folder"),
        name: str = typer.Option(None, "--name", "-n", help="Package name (default: folder name)"),
        version: str = typer.Option("0.1.0", "--version", "-v", help="Package version")
):
    """
    Wrap an existing directory as a Nexon package.
    """
    pm = PackageManager()
    try:
        pkgver = pm.wrap_tool(source_path, name=name, version=version)
        typer.secho(f"Wrapped tool: {pkgver}", fg="green")
    except Exception as e:
        typer.secho(f"Error wrapping tool: {e}", fg="red")
        raise typer.Exit(1)
