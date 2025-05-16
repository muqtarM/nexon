import subprocess

import typer
import requests
from nexon_cli.core.configs import config

app = typer.Typer(help="Browse & install micro-tools")

SERVER = config.server_url.rstrip("/")


@app.command("list")
def mk_list():
    resp = requests.get(f"{SERVER}/marketplace")
    resp.raise_for_status()
    for i in resp.json():
        typer.echo(f"{i['name']}:{i['version']}   - {i['description']}")


@app.command("install")
def mk_install(name: str, version:str):
    # simple pip install of a named package, or git clone as needed
    url = f"{SERVER}/marketplace/{name}/{version}"
    resp = requests.get(url)
    resp.raise_for_status()
    meta = resp.json().get("metadata", {})
    cmd = meta.get("install_command")
    if not cmd:
        typer.secho("No install command defined", fg="red")
        raise typer.Exit(1)
    typer.secho(f"Running: {cmd}", fg="cyan")
    subprocess.run(cmd, shell=True, check=True)
    typer.secho("Tool installed", fg="green")
