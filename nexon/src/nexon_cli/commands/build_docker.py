import typer
from nexon_cli.core.docker_builder import build_docker_image, DockerBuildError


def build_docker_cmd(
        env_name: str = typer.Argument(..., help="Name of the environment to containerize"),
        tag: str = typer.Option(None, "--tag", "-t", help="Optional Docker image tag")
):
    """
    Build a Docker image for the specified environment.
    """
    try:
        image = build_docker_image(env_name, tag)
    except DockerBuildError as e:
        typer.secho(f"Docker build failed: {e}", fg="red")
        raise typer.Exit(1)
    else:
        typer.secho(f"Docker image built: {image}", fg="green")
