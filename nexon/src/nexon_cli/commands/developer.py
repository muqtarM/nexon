import typer, requests
from nexon_cli.core.configs import config

app = typer.Typer(help="Community Developer Portal")

SERVER = config.server_url.rstrip("/")
HEADERS = lambda: {"Authorization": f"Bearer {config.cli_token}"}


@app.command("submit-plugin")
def submit_plugin(
        name: str = typer.Argument(...),
        repo: str = typer.Argument(...),
        author: str = typer.Option(..., "--author"),
        desc: str = typer.Option(None, "--desc")
):
    r = requests.post(
        f"{SERVER}/developer/plugins",
        json={"name": name, "repo_url": repo, "author": author, "description": desc},
        headers=HEADERS()
    )
    r.raise_for_status()
    data = r.json()
    typer.secho(f"Submission ID: {data['id']} (status: {data['status']})", fg="green")


@app.command("list-submissions")
def list_submissions():
    r = requests.get(f"{SERVER}/developer/plugins", headers=HEADERS())
    r.raise_for_status()
    for s in r.json():
        typer.echo(f"{s['id']} {s['name']} [{s['status']}] by {s['author']}")


@app.command("review")
def review(
        submission_id: str = typer.Argument(...),
        approve: bool = typer.Option(..., "--approve/--reject")
):
    r = requests.post(
        f"{SERVER}/developer/plugins/{submission_id}/review",
        params={"approve": approve},
        headers=HEADERS()
    )
    r.raise_for_status()
    s = r.json()
    typer.secho(f"{s['name']} => {s['status']} by {s['reviewer']}", fg="green")
