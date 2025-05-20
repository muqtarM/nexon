# nexon_cli/commands/run.py

import os
import shlex
import subprocess
import typer
from nexon_cli.core.env_manager import EnvironmentManager
from nexon_cli.core.package_manager import PackageManager

app = typer.Typer()


def run_cmd(
    env: str = typer.Argument(..., help="Environment to activate"),
    name: str = typer.Argument(..., help="Command name from package recipes"),
    *extra: str  # collects any additional args
):
    """
    Activate <env>, look up the '<name>' entry under each package's `commands:`,
    and execute it (with any extra args appended).
    """
    # 1) Activate the env
    em = EnvironmentManager()
    em.activate_environment(env)

    # 2) Gather all commands from installed packages
    pm = PackageManager()
    pkg_list = em.get_environment(env)["packages"]
    recipes = pm.load_recipes(pkg_list)   # returns dict[name][cmd_name] → cmd_str

    # 3) Find the first recipe that defines this command
    cmd_tpl = None
    pkg_found = None
    for pkg, cmds in recipes.items():
        if name in cmds:
            cmd_tpl = cmds[name]
            pkg_found = pkg
            break

    if not cmd_tpl:
        typer.secho(f"No command '{name}' found in {pkg_list}", fg="red")
        raise typer.Exit(1)

    # 4) Fill in any template fields (e.g. {scene}, {root}, etc.)
    context = {"env": env, **os.environ}
    cmd = cmd_tpl.format(**context)
    # 5) Append extra args
    if extra:
        cmd += " " + " ".join(shlex.quote(a) for a in extra)

    typer.secho(f"🔧 [{pkg_found}] Running: {cmd}", fg="cyan")
    # 6) Run it
    subprocess.run(cmd, shell=True, check=True)
