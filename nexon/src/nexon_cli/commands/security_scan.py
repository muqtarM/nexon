import typer
from nexon_cli.core.security_manager import SecurityManager, SecurityError


def security_scan(
        env_name: str = typer.Argument(..., help="Environment to scan for issues")
):
    """
    Scan the specified environment for policy violations and known vulnerabilities.
    """
    sm = SecurityManager()
    try:
        issues = sm.scan_environment(env_name)
    except Exception as e:
        typer.secho(f"Error during security scan: {e}", fg="red")
        raise typer.Exit(1)

    if not issues:
        typer.secho(f"No security issues found in environment '{env_name}'", fg="green")
        return
    typer.secho(f"Security issues found in '{env_name}':", fg="yellow")
    for item in issues:
        typer.echo(f"    - {item}")
    raise typer.Exit(1)
