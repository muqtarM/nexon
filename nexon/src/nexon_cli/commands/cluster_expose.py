import typer
from nexon_cli.core.cluster_manager import ClusterManager, ClusterError


def cluster_expose(
        env_name: str = typer.Argument(..., help="Env to expose via Ingress"),
        host: str = typer.Argument(..., help="Hostname for the Ingress rule"),
        path: str = typer.Option("/", "--path", help="HTTP path prefix"),
        namespace: str = typer.Option(None, "--namespace", "-n"),
        port: int = typer.Option(80, "--port", help="Service port")
):
    """
    Create/update an Ingress mapping host/path -> your service.
    """
    mgr = ClusterManager()
    try:
        out = mgr.create_ingress(env_name, host, path, namespace, port)
        typer.secho(f"Ingress '{out['ingress']}' at {out['host']}{path}", fg="green")
    except ClusterError as e:
        typer.secho(f"Ingress failed: {e}", fg="red")
        raise typer.Exit(1)
