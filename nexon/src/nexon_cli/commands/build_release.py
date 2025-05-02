import subprocess
import typer


def build_release():
    """
    Build source & wheel, publish to PyPI, and build & push Docker image.
    Requires GITHUB_TOKEN / DOCKERHUB creds in env.
    """
    typer.secho("Building Python distribution...", fg="cyan")
    subprocess.run(["python", "-m", "build"], check=True)

    typer.secho("Uploading to PYPI...", fg="cyan")
    subprocess.run(["twine", "upload", "dist/*"], check=True)

    # Get version from latest Git tag
    tag = subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"]).strip().decode()
    image = f"nexon/cli:{tag.lstrip('v')}"
    typer.secho(f"Building Docker image {image}...", fg="cyan")
    subprocess.run(["docker", "build", "-t", image, "."], check=True)

    typer.secho(f"Pushing Docker image {image}...", fg="cyan")
    subprocess.run(["docker", "push", image], check=True)

    typer.secho("Release published!", fg="green")
