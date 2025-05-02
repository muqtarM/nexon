import typer
from nexon_cli.core.env_manager import EnvironmentManager


def env_file(
    env_name: str = typer.Argument(..., help="Environment name to export"),
    output: str = typer.Option(
        None, "--output", "-o", help="Path to write to .env file (default: stdout)"
    )
):
    """
    Export environment variables for a Nexon env into dotenv format.
    """
    em = EnvironmentManager()
    try:
        result = em.export_env_file(env_name, output_path=output)
    except Exception as e:
        typer.secho(f"Error exporting env file: {e}", fg="red")
        raise typer.Exit(1)

    if output:
        typer.secho(f"Written env file to {result}", fg="green")
    else:
        typer.echo(result)
