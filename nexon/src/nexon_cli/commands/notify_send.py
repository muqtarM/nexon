import typer
import requests
from nexon_cli.core.configs import config

app = typer.Typer(help="Send real-time notifications to the web dashboard")


def send(
        title: str = typer.Argument(..., help="Notification title"),
        message: str = typer.Argument(..., help="Notification body"),
        level: str = typer.Option("info", "--level", "-l", help="info|success|warning|error")
):
    """
    POST to the server to broadcast a toast to all connected UIs
    """
    url = config.server_url.rstrip("/") + "/notifications/send"
    headers = {"Authorization": f"Bearer {config.cli_token}"}
    payload = {"title": title, "message": message, "level": level}
    resp = requests.post(url, json=payload, headers=headers)
    if resp.status_code == 200:
        typer.secho("Notification sent", fg="green")
    else:
        typer.secho(f"Failed to send ({resp.status_code})", fg="red")
        raise typer.Exit(1)


app.command("send")(send)
