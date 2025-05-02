import typer
from typing import Optional
from nexon_cli.core.build_manager import build_manager


def build_docker(
        env_name: str,
        tag: Optional[str] = typer.Option(None, help="Docker image tag (default: nexon/<env_name>:latest")
):
    """
    Build a Docker image for the specified environment.
    """
    try:
        build_manager.build_docker_image(env_name, tag)
    except Exception as e:
        typer.secho(f"Error building Docker for '{env_name}': {e}", fg="red")
        raise typer.Exit(1)
