import typer
from nexon_cli.core.policy_manager import PolicyManager, PolicyError


def policy_validate(env: str):
    """
    Validate an environment against your policy-as-code rules.
    """
    try:
        pm = PolicyManager()
    except PolicyError as e:
        typer.secho(f"❌ {e}", fg="red")
        raise typer.Exit(1)

    violations = pm.validate(env)
    if not violations:
        typer.secho(f"✔ '{env}' is compliant.", fg="green")
        return
    typer.secho(f"⚠ Found {len(violations)} policy violations:", fg="yellow")
    for v in violations:
        typer.echo(f"  • [{v['rule_id']}] {v['description']} — {v.get('details')}")
    raise typer.Exit(2)
