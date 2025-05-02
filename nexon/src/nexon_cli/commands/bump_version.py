import re
import subprocess
import typer
from pathlib import Path

VERSION_FILE = Path(__file__).parent.parent.parent.parent / "pyproject.toml"


def bump_version(
        new_version: str = typer.Argument(..., help="New semantic version, e.g. 1.2.3")
):
    """
    Update the version in pyproject.toml, commit, and tag Git.
    """
    # 1) Update pyproject.toml
    text = VERSION_FILE.read_text(encoding="utf-8")
    new_text, count = re.subn(
        r'^(version\s*=\s*)".+"',
        rf'\1"{new_version}"',
        text,
        flags=re.MULTILINE
    )
    if count == 0:
        typer.secho("Failed to find version line in pyproject.toml", fg="red")
        raise typer.Exit(1)
    VERSION_FILE.write_text(new_text, encoding="utf-8")
    typer.secho(f"Bumped version to {new_version} in pyproject.toml", fg="green")

    # 2) Commit & Tag
    subprocess.run(["git", "add", str(VERSION_FILE)], check=True)
    subprocess.run(["git", "commit", "-m", f"Bump version to {new_version}"], check=True)
    subprocess.run(["git", "tag", f"v{new_version}"], check=True)
    typer.secho(f"Created Git tag v{new_version}", fg="green")
