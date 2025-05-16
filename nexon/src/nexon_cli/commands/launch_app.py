# nexon_cli/commands/launch_app.py

import typer
import subprocess
import webbrowser
import sys
import os
from threading import Thread
from time import sleep


def _run_uvicorn(host: str, port: int):
    """
    Launches the FastAPI app via uvicorn.
    """
    cmd = [
        sys.executable, "-m", "uvicorn",
        "app.main:app",
        "--host", host,
        "--port", str(port),
        "--reload"
    ]
    # Inherit STDIO so logs show up
    subprocess.run(cmd, check=True)


def launch_app(
    host: str = typer.Option("127.0.0.1", "--host", "-h", help="Host to bind the server"),
    port: int = typer.Option(8000, "--port", "-p", help="Port to bind the server"),
    no_browser: bool = typer.Option(False, "--no-browser", help="Do not open the browser automatically")
):
    """
    Launch the Nexon web dashboard (FastAPI + D3 graph).
    """
    # 1) Optionally open the default browser after a short delay
    if not no_browser:
        url = f"http://{host}:{port}/static/index.html"
        def _open():
            sleep(1.5)
            webbrowser.open(url)
        Thread(target=_open, daemon=True).start()

    # 2) Run uvicorn (will block)
    typer.secho(f"🚀 Starting Nexon dashboard at http://{host}:{port}", fg="green")
    _run_uvicorn(host, port)
