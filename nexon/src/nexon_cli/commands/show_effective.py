import typer
import yaml

from nexon_cli.core.layer_manager import layer_manager


def show_effective(
        env: str = typer.Argument(..., help="Environment name"),
        team: str = typer.Argument(..., help="Team name"),
        project: str = typer.Argument(..., help="Project name"),
        user: str = typer.Option(None, "--user", "-u", help="Username (defaults to current user)"),
):
    """
    Show the merged (effective) configuration for a given
    environment, layering global->team->project->user->env.
    """
    merged = layer_manager.get_effective(env, team, project, user)
    typer.echo(yaml.safe_dump(merged))
