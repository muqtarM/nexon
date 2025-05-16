import typer
from nexon_cli.core.plugin_lifecycle import (
    PluginLifecycleError, PluginLifecycleManager
)

app = typer.Typer(help="Manage Nexon plugins")


def install(
        path: str = typer.Option(
            None, "--path", "-p", help="Local folder containing plugin.yaml"
        ),
        git: str = typer.Option(
            None, "--git", "-g", help="Git URL of plugin repo"
        )
):
    """
    Install a plugin from a local path or Git URL
    """
    mgr = PluginLifecycleManager()
    if not (path or git):
        typer.secho("Error: specify --path or --git", fg="red")
        raise typer.Exit(1)
    try:
        name = mgr.install_from_path(path) if path else mgr.install_from_git(git)
        typer.secho(f"Installed plugin '{name}'", fg="green")
    except PluginLifecycleError as e:
        typer.secho(f"{e}", fg="red")
        raise typer.Exit(1)


def update(
        name: str = typer.Argument(..., help="Plugin name to update")
):
    """
    Update a plugin (Git-based plugins only).
    """
    mgr = PluginLifecycleManager()
    try:
        mgr.update_plugin(name)
    except PluginLifecycleError as e:
        typer.secho(f"{e}", fg="red")
        raise typer.Exit(1)


def uninstall(
        name: str = typer.Argument(..., help="Plugin name to remove")
):
    """
    Uninstall a plugin by name.
    """
    mgr = PluginLifecycleManager()
    try:
        mgr.uninstall_plugin(name)
    except PluginLifecycleError as e:
        typer.secho(f"{e}", fg="red")
        raise typer.Exit(1)


def list_all():
    """
    List all installed plugins and their metadata
    """
    mgr = PluginLifecycleManager()
    plugins = mgr.list_plugins()
    if not plugins:
        typer.echo("No plugins installed.")
        return
    for p in plugins:
        typer.secho(f"- {p['name']} (v{p.get('version', '?')})", fg="cyan")
        typer.echo(f"    path: {p['path']}")
        desc = p.get("description")
        if desc:
            typer.echo(f"    desc: {desc}")


# Register in main CLI
app.command("install")(install)
app.command("update")(update)
app.command("uninstall")(uninstall)
app.command("list")(list_all)
