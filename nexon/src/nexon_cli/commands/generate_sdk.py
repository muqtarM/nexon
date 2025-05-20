import typer
import subprocess
from pathlib import Path
from nexon_cli.core.configs import config

app = typer.Typer(help="Generate SDK client from Nexon OpenAPI spec")


@app.command("generate-sdk")
def generate_sdk(
    lang: str = typer.Option("python", "--lang", "-l", help="Target language (python, typescript)"),
    output: Path = typer.Option(Path("sdk-client"), "--output", "-o", help="Output directory")
):
    """
    Fetch the live OpenAPI spec from the server and invoke openapi-python-client
    (or equivalent for other languages) to generate a client SDK.
    """
    spec_url = f"{config.server_url.rstrip('/')}/openapi.json"
    output.mkdir(parents=True, exist_ok=True)
    if lang == "python":
        cmd = [
            "openapi-python-client",
            "generate",
            "--url", spec_url,
            "--output", str(output)
        ]
    else:
        typer.secho(f"Language '{lang}' not supported yet.", fg="red")
        raise typer.Exit(1)

    typer.secho(f"🔧 Running: {' '.join(cmd)}", fg="cyan")
    subprocess.run(cmd, check=True)
    typer.secho(f"✅ SDK generated in {output}", fg="green")
