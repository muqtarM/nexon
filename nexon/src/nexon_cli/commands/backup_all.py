# nexon_cli/commands/backup_all.py

import typer
from nexon_cli.core.backup_manager import BackupManager, BackupError


def backup_all_cmd():
    """
    Create a full Nexon backup (DB + envs + packages + layers).
    """
    mgr = BackupManager()
    try:
        archive = mgr.backup_all()
        typer.secho(f"✅ Backup saved to {archive}", fg="green")
    except BackupError as e:
        typer.secho(f"❌ Backup failed: {e}", fg="red")
        raise typer.Exit(1)
