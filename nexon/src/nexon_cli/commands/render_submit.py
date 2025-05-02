import typer
from nexon_cli.core.render_manager import render_manager, RenderError


def submit_render_cmd(
        env_name: str = typer.Argument(..., help="Environment to use"),
        scene_file: str = typer.Argument(..., help="Path to the scene file"),
        farm: str = typer.Option("deadline", help="Render farm identifier"),
        options: str = typer.Option(None, help="Additional farm options")
):
    """
    Submit a render job to the farm
    """
    try:
        msg = render_manager.submit_render(env_name, scene_file, farm, options)
        typer.secho(f"{msg}", fg="green")
    except RenderError as e:
        typer.secho(f"{e}", fg="red")
        raise typer.Exit(1)
