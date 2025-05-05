import typer
from nexon_cli.core.cluster_manager import ClusterManager, ClusterError


def cluster_list(
        namespace: str = typer.Option(None, "--namespace", "-n", help="Filter bu namespace")
):
    """
    List all Nexon deployments and their replica counts
    """
    mgr = ClusterManager()
    try:
        entries = mgr.list(namespace)
        for name, ns, avail in entries:
            typer.echo(f"{ns}/{name} -> {avail} replicas")
    except ClusterError as e:
        typer.secho(f"List failed: {e}", fg="red")
        raise typer.Exit(1)
