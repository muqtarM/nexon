import typer
import subprocess
from nexon_cli.core.configs import config


def p4_sync_cmd(
        path: str = typer.Argument(..., help="Perforce depot path to sync")
):
    cmd = [
        "p4",
        "-p", config.p4_port,
        "-u", config.p4_user,
        "-c", config.p4_client,
        "sync", path
    ]
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        typer.secho(f"Perforce sync failed: {result.stderr}", fg="red")
        raise typer.Exit(1)
    typer.secho(f"Synced: {result.stdout}", fg="green")
