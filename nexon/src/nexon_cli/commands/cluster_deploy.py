import typer
from nexon_cli.core.cluster_manager import ClusterManager, ClusterError


def parse_env_vars(pairs: list[str]) -> dict[str, str]:
    out = {}
    for kv in pairs:
        if "=" not in kv:
            typer.secho(f"Invalid env var '{kv}', expected KEY=VAL", fg="red")
            raise typer.Exit(1)
        k, v = kv.split("=", 1)
        out[k] = v
    return out


def cluster_deploy(
        env_name: str = typer.Argument(..., help="Nexon env to deploy"),
        namespace: str = typer.Option(None, "--namespace", "-n"),
        image: str = typer.Option(None, "--image"),
        replicas: int = typer.Option(1, "--replicas", "-r"),
        cpu: str = typer.Option("500m", "--cpu"),
        memory: str = typer.Option("1Gi", "--memory"),
        envs: list[str] = typer.Option([], "--env", "-e", help="Env-var injection, KEY=VAL")
):
    """
    Deploy or update a Kubernetes Deployment & Service for your Nexon environment,
    with optional env-vars
    """
    mgr = ClusterManager()
    env_vars = parse_env_vars(envs)
    try:
        info = mgr.deploy(env_name, namespace, image, cpu, memory, replicas, env_vars)
        typer.secho(f"{info['namespace']} -> {info['image']} @ {info['replicas']} replicas", fg="green")
    except ClusterError as e:
        typer.secho(f"Deployment failed: {e}", fg="red")
        raise typer.Exit(1)
