import typer
from nexon_cli.core.cluster_manager import ClusterManager, ClusterError


def cluster_autoscale(
        env_name: str = typer.Argument(...),
        min_replicas: int = typer.Option(..., help="Minimum replicas"),
        max_replicas: int = typer.Option(..., help="Maximum replicas"),
        cpu_pct: int = typer.Option(80, "--cpu-percent"),
        namespace: str = typer.Option(None, "--namespace", "-n")
):
    mgr = ClusterManager()
    try:
        out = mgr.autoscale(env_name, min_replicas, max_replicas, cpu_pct, namespace)
        typer.secho(f"HPA '{out['hpa']}' {out['min']}-{out['max']} @ {cpu_pct}%", fg="green")
    except ClusterError as e:
        typer.secho(f"Autoscale failed: {e}", fg="red")
        raise typer.Exit(1)
