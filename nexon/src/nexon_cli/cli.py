# nexon_cli/cli.py

import typer

# Core commands
from nexon_cli.commands.create_env import create_env
from nexon_cli.commands.activate_env import activate_env
from nexon_cli.commands.deactivate_env import deactivate_env
from nexon_cli.commands.diff_env import diff_env
from nexon_cli.commands.wrap_tool import wrap_tool

from nexon_cli.commands.build_docker import build_docker_cmd

from nexon_cli.commands.install_package import install_package
from nexon_cli.commands.uninstall_package import uninstall_package
from nexon_cli.commands.list_envs import list_envs
from nexon_cli.commands.list_packages import list_packages
from nexon_cli.commands.detect_hardware import detect_hardware
# from nexon_cli.commands.launch_app import launch_app

# Workspace commands
from nexon_cli.commands.workspace_create import workspace_create
from nexon_cli.commands.workspace_link import workspace_link
from nexon_cli.commands.workspace_list import workspace_list

# Recipe commands
from nexon_cli.commands.list_recipes import list_recipes_cmd
from nexon_cli.commands.apply_recipe import apply_recipe_cmd

# Package commands
from nexon_cli.commands.create_package import create_package_cmd

# Lock and build
from nexon_cli.commands.lock_env import lock_env
from nexon_cli.commands.build_package import build_package_cmd

from nexon_cli.commands.render_submit import submit_render_cmd
from nexon_cli.commands.ci_run import ci_run_cmd

# Layers commands
from nexon_cli.commands.create_layer import create_layer
from nexon_cli.commands.list_layers import list_layers
from nexon_cli.commands.show_effective import show_effective

from nexon_cli.commands.shell import shell_cmd
from nexon_cli.commands.completion import completion

from nexon_cli.commands.env_file import env_file

from nexon_cli.commands.bump_version import bump_version
from nexon_cli.commands.build_release import build_release

from nexon_cli.commands.security_scan import security_scan

cli = typer.Typer(help="Nexon: Next-Gen Multimedia Environment Manager")

# Register commands
cli.command(name="create-env")(create_env)
cli.command(name="activate-env")(activate_env)
cli.command(name="deactivate-env")(deactivate_env)
cli.command(name="diff-env")(diff_env)

cli.command(name="build-package")(build_package_cmd)
cli.command(name="build-docker")(build_docker_cmd)
cli.command(name="wrap-tool")(wrap_tool)

cli.command(name="create-package")(create_package_cmd)
cli.command(name="install-package")(install_package)
cli.command(name="uninstall-package")(uninstall_package)

cli.command(name="list-envs")(list_envs)
cli.command(name="list-packages")(list_packages)

cli.command(name="detect-hardware")(detect_hardware)
# cli.command(name="launch-app")(launch_app)

cli.command(name="workspace-create")(workspace_create)
cli.command(name="workspace-link")(workspace_link)
cli.command(name="workspace-list")(workspace_list)

cli.command(name="list-recipes")(list_recipes_cmd)
cli.command(name="apply-recipe")(apply_recipe_cmd)

cli.command(name="lock-env")(lock_env)
cli.command(name="env-file")(env_file)

cli.command(name="render-submit")(submit_render_cmd)
cli.command(name="ci-run")(ci_run_cmd)

cli.command(name="create-layer")(create_layer)
cli.command(name="list-layers")(list_layers)
cli.command(name="show-effective")(show_effective)

cli.command(name="shell")(shell_cmd)
cli.command(name="completion")(completion)

cli.command(name="bump-version")(bump_version)
cli.command(name="build-release")(build_release)

cli.command(name="security-scan")(security_scan)

# Entry point
if __name__ == '__main__':
    cli()
