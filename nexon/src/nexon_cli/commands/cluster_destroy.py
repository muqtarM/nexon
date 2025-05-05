import typer
from nexon_cli.core.cluster_manager import ClusterManager, ClusterError


def cluster_destroy(
        env_name: str = typer.Argument(..., help="Nexon env to tear down"),
        namespace: str = typer.Option(None, "--namespace", "-n")
):
    """
    Destroy the Deployment & Service for the given environment.
    """
    mgr = ClusterManager()
    try:
        mgr.destroy(env_name, namespace)
        typer.secho(f"Destroyed '{env_name}' in '{namespace or env_name}'", fg="green")
    except ClusterError as e:
        typer.secho(f"Destroy failed: {e}", fg="red")
        raise typer.Exit(1)
