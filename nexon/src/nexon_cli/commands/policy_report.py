import typer
from pathlib import Path
from nexon_cli.core.policy_manager import PolicyManager, PolicyError


def policy_report(
    env: str = typer.Argument(...),
    output: str = typer.Option("policy_report.html", "--output", "-o")
):
    """
    Generate a full HTML compliance report for an environment.
    """
    try:
        pm = PolicyManager()
    except PolicyError as e:
        typer.secho(f"❌ {e}", fg="red")
        raise typer.Exit(1)

    violations = pm.validate(env)
    out_path = Path(output)
    pm.render_report(env, violations, out_path)
