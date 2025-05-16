import typer
import requests
from nexon_cli.core.configs import config
from datetime import datetime

app = typer.Typer(help="Manage studio licenses")

SERVER = config.server_url.rstrip("/")


def issue(
        studio: str = typer.Argument(...),
        tier: str = typer.Argument(..., help="free|pro|enterprise"),
        quotas: list[str] = typer.Option(..., "--quota", "-q", help="feature=limit"),
        valid_days: int = typer.Option(None, "--days")
):
    """
    Issue a new license key for a studio
    """
    q = dict(kv.split("=", 1) for kv in quotas)
    resp = requests.post(
        f"{SERVER}/licenses",
        json={"studio": studio, "tier": tier, "quotas": q, "valid_days": valid_days},
        headers={"Authorization": f"Bearer {config.cli_token}"}
    )
    resp.raise_for_status()
    data = resp.json()
    typer.secho(f"Key: {data['key']}", fg="green")
    typer.echo(f"Studio: {data['studio']} Tier: {data['tier']}")
    typer.echo(f"Quotas: {data['quotas']} Expires: {data['expires_at']}")


app.command("issue")(issue)
