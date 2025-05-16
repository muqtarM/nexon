import typer
from pathlib import Path
from nexon_cli.core.pipeline_manager import PipelineManager

app = typer.Typer()


@app.command("list-templates")
def list_templates():
    pm = PipelineManager(Path("nexon_templates"))
    for t in pm.list_templates():
        typer.echo(f"- {t}")


@app.command("init")
def pipeline_init(
        template: str = typer.Argument(...),
        name: str = typer.Argument(..., help="New project folder")
):
    pm = PipelineManager(Path("nexon_templates"))
    pm.render(template, Path(name), {"project_name": name})
    typer.secho(f"Created project '{name}' from '{template}'", fg="green")
