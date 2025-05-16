import typer
from pathlib import Path
from nexon_cli.core.python_importer import PythonPackageImporter, PythonImporterError


def import_wheel(
        wheel_path: Path = typer.Argument(..., exists=True, help="Path to .whl or .tar.gz"),
        include_deps: bool = typer.Option(
            False, "--include-deps", "-d",
            help="Also import Requires-Dist dependencies recursively"
        )
):
    """
    Register a local wheel/sdist and (optionally) its dependencies.
    """
    imp = PythonPackageImporter()
    try:
        imported = imp.import_from_file(wheel_path, include_deps=include_deps)
        for pkgver in imported:
            typer.secho(f"Imported {pkgver}", fg="green")
    except PythonImporterError as e:
        typer.secho(f"Import failed: {e}", fg="red")
        raise typer.Exit(1)
