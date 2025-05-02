# Updated nexon_cli/commands/shell.py

import os
import subprocess
import sys
import typer
from nexon_cli.core.env_manager import EnvironmentManager

def shell_cmd(
    env_name: str = typer.Argument(..., help="Name of the environment to activate"),
    shell_path: str = typer.Option(
        None, "--shell", "-s", help="Shell binary to launch (defaults to your system shell)"
    )
):
    """
    Launch an interactive shell with the specified Nexon environment activated.
    """
    em = EnvironmentManager()
    # Activate the environment (sets env-vars in os.environ)
    em.activate_environment(env_name)

    # Determine default shell based on platform
    if shell_path:
        shell = shell_path
    else:
        if sys.platform.startswith("win"):
            # On Windows, use COMSPEC (cmd.exe) or PowerShell
            shell = os.environ.get("COMSPEC") or os.environ.get("SHELL") or "cmd.exe"
        else:
            # On POSIX, prefer $SHELL fallback to /bin/bash
            shell = os.environ.get("SHELL") or "/bin/bash"

    typer.secho(f"🔀 Spawning '{shell}' with environment '{env_name}'…", fg="green")
    try:
        # Launch the shell; on Windows COMSPEC expects string, on POSIX list works too
        if sys.platform.startswith("win"):
            subprocess.run(shell, check=True, shell=True)
        else:
            subprocess.run([shell], check=True)
    except FileNotFoundError:
        typer.secho(f"❌ Shell executable not found: '{shell}'", fg="red")
        raise typer.Exit(1)
    except subprocess.CalledProcessError as e:
        typer.secho(f"❌ Subshell exited with code {e.returncode}", fg="red")
        raise typer.Exit(e.returncode)
