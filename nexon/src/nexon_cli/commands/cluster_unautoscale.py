import typer
from nexon_cli.core.cluster_manager import ClusterManager, ClusterError


def cluster_unautoscale(
        env_name: str = typer.Argument(...),
        namespace: str = typer.Option(None, "--namespace", "-n")
):
    mgr = ClusterManager()
    try:
        mgr.remove_autoscale(env_name, namespace)
        typer.secho(f"Removed HPA for '{env_name}'", fg="green")
    except ClusterError as e:
        typer.secho(f"Remove HPA failed: {e}", fg="red")
        raise typer.Exit(1)
