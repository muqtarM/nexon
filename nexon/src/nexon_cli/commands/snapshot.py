import typer
from nexon_cli.core.snapshot_manager import SnapshotManager

app = typer.Typer(help="Manage snapshots")


@app.command("create")
def create(name: str = typer.Argument(None)):
    sn = SnapshotManager().create(name)
    typer.secho(f"Snapshot '{sn}' created", fg="green")


@app.command("list")
def list_():
    for sn in SnapshotManager().list():
        typer.echo(sn)


@app.command("restore")
def restore(name: str):
    SnapshotManager().restore(name)
    typer.secho("Restored", fg="green")
