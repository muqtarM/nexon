import os.path

import typer
import yaml
from nexon_cli.core.layer_manager import layer_manager, LayerError


def create_layer(
        level: str = typer.Argument(..., help="global|team|project|user"),
        args: list[str] = typer.Argument(...,
                                         help="For global: <spec_file>.For team/project/user: <name> <spec_file>")
):
    """
    Create or overwrite a configuration layer.
    """
    # Global layer: only spec file expected
    if level == "global":
        if len(args) != 1:
            typer.secho("Error: 'global' requires exactly 1 argument: <spec_file>", fg="red")
            raise typer.Exit(1)
        name = "_"  # ignored by LayerManager for global
        spec_file = args[0]

    # Other layers: name + spec_file
    elif level in ("team", "project", "user"):
        if len(args) != 2:
            typer.secho(f"Error: '{level}' requires 2 arguments: <name> <spec_file>", fg="red")
            raise typer.Exit(1)
        name, spec_file = args

    else:
        typer.secho(f"Error: Unknown layer level '{level}'", fg="red")
        raise typer.Exit(1)

    # If global spec file doesn't exist, create an empty one
    if level == "global" and not os.path.exists(spec_file):
        try:
            dirpath = os.path.dirname(spec_file)
            if dirpath:
                os.makedirs(dirpath, exist_ok=True)
            with open(spec_file, "w", encoding="utf-8") as f:
                yaml.safe_dump({}, f)
            typer.secho(f"Spec file '{spec_file}' note found; created empty spec file.", fg="yellow")
        except Exception as e:
            typer.secho(f"Failed to create spec file '{spec_file}': {e}", fg="red")
            raise typer.Exit(1)

    # Load spec and delegate
    try:
        with open(spec_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
    except Exception as e:
        typer.secho(f"Failed to read spec file: {e}", fg="red")
        raise typer.Exit(1)

    try:
        layer_manager.create_layer(level, name, data)
    except LayerError as e:
        typer.secho(f"Error creating layer: {e}", fg="red")
        raise typer.Exit(1)

    # Delegate to layer manager
    try:
        layer_manager.create_layer(level, name, data)
    except LayerError as e:
        typer.secho(f"Error creating layer: {e}", fg="red")
        raise typer.Exit(1)

    typer.secho(f"Layer '{level}' written successfully.", fg="green")
