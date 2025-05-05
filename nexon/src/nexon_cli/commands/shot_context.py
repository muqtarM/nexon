import typer
from nexon_cli.core.configs import config
from urllib.parse import urljoin
import requests

app = typer.Typer()


def shot_context_cmd(
        shot: str = typer.Argument(..., help="Shot name to query")
):
    url = config.shotgrid_url.rstrip("/") + "/api/v1/entity/Shot"
    params = {
        "filters": [["code", "is", shot]],
        "fields": ["id", "code", "project", "status_list"],
        "limit": 1
    }
    resp = requests.get(url, auth=(config.shotgrid_script, config.shotgrid_key), params=params)
    if resp.status_code != 200 or not resp.json().get("data"):
        typer.secho(f"Shot '{shot}' not found", fg="red")
        raise typer.Exit(1)
    data = resp.json()["data"][0]
    typer.echo(f"Shot {data['code']} (ID: {data['id']}) in project {data['project']['name']}")
