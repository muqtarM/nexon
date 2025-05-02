import typer
from nexon_cli.core.layer_manager import layer_manager


def list_layers():
    """
    List all defined configuration layers (global, team, project, user).
    """
    layers = layer_manager.list_layers()
    for lvl, names in layers.items():
        display = ", ".join(names) if names else "<none>"
        typer.echo(f"{lvl}: {display}")
