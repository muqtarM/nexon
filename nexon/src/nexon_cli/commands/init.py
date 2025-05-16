import sys

import typer, subprocess, os
from pathlib import Path

app = typer.Typer()


@app.command("init")
def quickstart(
        name: str,
        template: str = typer.Option(None, "--template", "-t", help="Pipeline template"),
        git: bool = typer.Option(False, "--git/--no-git" )
):
    """
    Quickstart a new Nexon project (scaffold files, git, venv).
    """
    # 1) scaffold pipeline
    if template:
        from nexon_cli.commands.pipeline import pipeline_init
        pipeline_init(template, name)
    Path(name).mkdir(exist_ok=True)
    os.chdir(name)
    # 2) git init
    if git:
        subprocess.run(["git", "init"], check=True)
        typer.echo("Initialized Git repository")
    # 3) venv
    subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    typer.secho(f"Project '{name}' ready", fg="green")
