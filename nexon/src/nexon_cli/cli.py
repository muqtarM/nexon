# nexon_cli/cli.py
import time

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
from nexon_cli.commands.launch_app import launch_app

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

from nexon_cli.commands.shot_context import shot_context_cmd
from nexon_cli.commands.p4_sync import p4_sync_cmd

from nexon_cli.commands.cluster_deploy import cluster_deploy
from nexon_cli.commands.cluster_destroy import cluster_destroy
from nexon_cli.commands.cluster_list import cluster_list

from nexon_cli.commands.cluster_expose import cluster_expose
from nexon_cli.commands.cluster_autoscale import cluster_autoscale
from nexon_cli.commands.cluster_unautoscale import cluster_unautoscale

from nexon_cli.commands.policy_validate import policy_validate
from nexon_cli.commands.policy_report import policy_report

from nexon_cli.commands.backup_all import backup_all_cmd
from nexon_cli.commands.restore_backup import restore_cmd
from nexon_cli.commands.backup_schedule import backup_schedule_cmd

from nexon_cli.commands.run import run_cmd

from nexon_cli.commands.import_pypi import import_pypi
from nexon_cli.commands.import_wheel import import_wheel

import nexon_cli.commands.plugin as plugin_cmds
import nexon_cli.commands.token as token_cmds
import nexon_cli.commands.notify_send as notify_cmds
import nexon_cli.commands.license as license_cmds
import nexon_cli. commands.marketplace as marketplace_cmds
import nexon_cli.commands.pipeline as pipeline_cmds
import nexon_cli.commands.init as init_cmds
import nexon_cli.commands.snapshot as snapshot_cmds

from nexon_cli.core.sentry_integration import init_sentry
from nexon_cli.core.metrics_cli import record_cli_metrics, push_metrics
from nexon_cli.core.tenant_manager import CLITenantManager

import nexon_cli.commands.tutorial as tutorial_cmds
import nexon_cli.commands.generate_sdk as generate_sdk_cmds

# before any commands run
init_sentry()

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

cli.command(name="shot-context")(shot_context_cmd)
cli.command(name="p4-sync")(p4_sync_cmd)

cli.command(name="cluster-deploy")(cluster_deploy)
cli.command(name="cluster-destroy")(cluster_destroy)
cli.command(name="cluster-list")(cluster_list)

cli.command(name="cluster-expose")(cluster_expose)

cli.command(name="cluster-autoscale")(cluster_autoscale)
cli.command(name="cluster-unautoscale")(cluster_unautoscale)

cli.command(name="policy-validate")(policy_validate)
cli.command(name="policy-report")(policy_report)

cli.command(name="backup-all")(backup_all_cmd)
cli.command(name="restore")(restore_cmd)
cli.command(name="backup-schedule")(backup_schedule_cmd)
cli.command(name="launch-app")(launch_app)

cli.command(name="run")(run_cmd)

cli.command(name="import-pypi")(import_pypi)
cli.command(name="import-wheel")(import_wheel)

cli.add_typer(plugin_cmds.app, name="plugin", help="Manage plugins")
cli.add_typer(token_cmds.app, name="token", help="Manage API tokens")
cli.add_typer(notify_cmds.app, name="notify", help="Broadcast real-time toasts")
cli.add_typer(license_cmds.app, name="license", help="Studio licensing")
cli.add_typer(marketplace_cmds.app, name="marketplace", help="Browse/install micro-tools")
cli.add_typer(pipeline_cmds.app, name="pipeline", help="Pipeline template")
cli.add_typer(init_cmds.app, name="init", help="Quickstart new project")
cli.add_typer(snapshot_cmds.app, name="snapshot", help="Snapshots (create/list/restore)")

cli.add_typer(tutorial_cmds.app, name="tutorial", help="Interactive in-terminal tutorial")
cli.add_typer(generate_sdk_cmds.app, name="generate-sdk", help="Generate SDK client from OpenAPI")


# @cli.callback(invoke_without_command=True)
# def main(tenant: str = typer.Option(None, "--tenant", "-t", help="Tenant ID")):
#     """
#     Nexon Cli entrypoint. Must specify --tenant or set NEXON_TENANT.
#     """
#     if tenant:
#         CLITenantManager.set_tenant(tenant)
#     else:
#         # will raise if not set in env
#         CLITenantManager.get_tenant()


# Entry point
if __name__ == '__main__':
    start = time.time()
    try:
        cli()
    finally:
        dur = time.time() - start
        record_cli_metrics("main", dur)
        push_metrics()
