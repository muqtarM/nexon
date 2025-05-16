import typer
from nexon_cli.core.python_importer import PythonPackageImporter, PythonImporterError


def import_pypi(
        requirement: str = typer.Argument(..., help="PyPI requirement spec"),
        index_url: str = typer.Option(None, "--index-url"),
        extra_index_url: str = typer.Option(None, "--extra-index-url"),
        include_deps: bool = typer.Option(
            False, "--include-deps", "-d",
            help="Also import Requires-Dist dependencies recursively"
        )
):
    """
    Download from PyPI and register as one or more Nexon packages.
    """
    imp = PythonPackageImporter()
    try:
        imported = imp.import_from_pypi(
            requirement,
            index_url=index_url,
            extra_index_url=extra_index_url,
            include_deps=include_deps
        )
        for pkgver in imported:
            typer.secho(f"Imported {pkgver}", fg="green")
    except PythonImporterError as e:
        typer.secho(f"Import failed: {e}", fg="red")
        raise typer.Exit(1)
