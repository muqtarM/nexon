# nexon_cli/cli.py

import typer

from nexon_cli.commands.create_env import create_env
from nexon_cli.commands.activate_env import activate_env
from nexon_cli.commands.deactivate_env import deactivate_env
from nexon_cli.commands.install_package import install_package
from nexon_cli.commands.uninstall_package import uninstall_package
from nexon_cli.commands.list_envs import list_envs
from nexon_cli.commands.list_packages import list_packages
from nexon_cli.commands.detect_hardware import detect_hardware
from nexon_cli.commands.launch_app import launch_app
from nexon_cli.commands.workspace_create import workspace_create
from nexon_cli.commands.workspace_link import workspace_link

cli = typer.Typer(help="Nexon: Next-Gen Multimedia Environment Manager")

# CLI Command Hooks
cli.command()(create_env)
cli.command()(activate_env)
cli.command()(deactivate_env)
cli.command()(install_package)
cli.command()(uninstall_package)
cli.command()(list_envs)
cli.command()(list_packages)
cli.command()(detect_hardware)
cli.command()(launch_app)
cli.command()(workspace_create)
cli.command()(workspace_link)
