import typer
import requests
from datetime import datetime
from nexon_cli.core.configs import config

app = typer.Typer(help="Manage API tokens on Nexon server")

SERVER = config.server_url.rstrip("/")


def _auth_headers():
    if not config.cli_token:
        typer.secho("No CLI token configured. Set NEXON_CLI_TOKEN.", fg="red")
        raise typer.Exit(1)
    return {"Authorization": f"Bearer {config.cli_token}"}


@app.command("create")
def token_create(
        scopes: list[str] = typer.Option(..., "--scope", "-s"),
        description: str = typer.Option(None, "--desc"),
        expires_in: int = typer.Option(None, "--expires-in", help="Seconds until expiry")
):
    """Create a new API token."""
    resp = requests.post(
        f"{SERVER}/auth/tokens",
        json={"scopes": scopes, "description": description, "expires_in": expires_in},
        headers=_auth_headers()
    )
    resp.raise_for_status()
    data = resp.json()
    typer.secho(f"Token: {data['token']}", fg="green")
    typer.secho(f"Scopes: {data['scopes']}", fg="cyan")
    typer.secho(f"Expires: {data['expires_at']}", fg="yellow")


@app.command("list")
def token_list():
    """List all API tokens."""
    resp = requests.get(f"{SERVER}/auth/tokens", headers=_auth_headers())
    resp.raise_for_status()
    for t in resp.json():
        typer.echo(f"- {t['token']} user={t['user']} scopes={t['scopes']} expires={t['expires_at']}")


@app.command("revoke")
def token_revoke(token: str = typer.Argument(..., help="Token to revoke")):
    """Revoke (delete) an API token."""
    resp = requests.delete(f"{SERVER}/auth/tokens/{token}", headers=_auth_headers())
    if resp.status_code == 404:
        typer.secho("Token not found", fg="red")
        raise typer.Exit(1)
    resp.raise_for_status()
    typer.secho("Token revoked", fg="green")
