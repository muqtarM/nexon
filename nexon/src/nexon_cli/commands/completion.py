# Updated nexon_cli/commands/completion.py

import typer

def completion(
    shell: str = typer.Argument(..., help="Shell to generate completion for"),
    install: bool = typer.Option(
        False, "--install", "-i",
        help="Install the completion script into your shell configuration"
    )
):
    """
    Generate—or install—shell completion code for Nexon.
    """
    try:
        import click_completion.core as cc
    except ImportError:
        typer.secho(
            "Error: click-completion is not installed. Install it with:\n"
            "  pip install click-completion",
            fg="red",
        )
        raise typer.Exit(1)

    # Determine supported shells
    supported = []
    shells_attr = getattr(cc, "shells", None)
    if callable(shells_attr):
        try:
            supported = shells_attr()
        except TypeError:
            supported = []
    elif isinstance(shells_attr, dict):
        supported = list(shells_attr.keys())
    elif isinstance(shells_attr, (list, tuple)):
        supported = list(shells_attr)

    if not supported:
        # Fallback list
        supported = ["bash", "zsh", "fish", "powershell"]

    shell = shell.lower()
    if shell not in supported:
        typer.secho(
            f"Error: Unsupported shell '{shell}'. Supported: {', '.join(supported)}",
            fg="red",
        )
        raise typer.Exit(1)

    prog = "nexon"

    if install:
        try:
            name, path = cc.install(shell=shell, prog_name=prog)
            typer.secho(f"✅ Installed '{name}' completion at {path}", fg="green")
        except Exception as e:
            typer.secho(f"Error installing completion: {e}", fg="red")
            raise typer.Exit(1)
    else:
        try:
            code = cc.get_code(shell=shell, prog_name=prog)
            typer.echo(code)
        except Exception as e:
            typer.secho(f"Error generating completion code: {e}", fg="red")
            raise typer.Exit(1)

