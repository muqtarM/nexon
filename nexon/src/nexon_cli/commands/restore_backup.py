# nexon_cli/commands/restore_backup.py

import typer
from nexon_cli.core.backup_manager import BackupManager, BackupError
from pathlib import Path


def restore_cmd(
    archive: str = typer.Argument(..., help="Path to backup .tar.gz")
):
    """
    Restore Nexon state from a backup archive.
    WARNING: this will overwrite your current data.
    """
    mgr = BackupManager()
    try:
        mgr.restore(archive)
        typer.secho("✅ Restore complete", fg="green")
    except BackupError as e:
        typer.secho(f"❌ Restore failed: {e}", fg="red")
        raise typer.Exit(1)
