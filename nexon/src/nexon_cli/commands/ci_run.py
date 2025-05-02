import typer
from nexon_cli.core.render_manager import render_manager, RenderError


def ci_run_cmd(
        env_name: str = typer.Argument(..., help="Environment to use"),
        script: str = typer.Argument(..., help="Path to the CI script to execute"),
        runner: str = typer.Option("github-actions", help="CI runner identifier")
):
    """
    Trigger a CI workflow for the given environment.
    """
    try:
        msg = render_manager.run_cli(env_name, script, runner)
        typer.secho(f"{msg}", fg="green")
    except RenderError as e:
        typer.secho(f"{e}", fg="red")
        raise typer.Exit(1)
