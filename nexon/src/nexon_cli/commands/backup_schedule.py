# Updated nexon_cli/commands/backup_schedule.py

import typer


def backup_schedule_cmd():
    """
    Show instructions for scheduling daily backups at 02:00 UTC via cron.
    """
    cron_line = "0 2 * * * nexon backup-all >> ~/.nexon/backups/backup.log 2>&1"
    typer.echo("\nTo schedule daily backups at 02:00 UTC, add this line to your crontab:\n")
    typer.secho(cron_line, fg="green")
    typer.echo("\nThen run:")
    typer.secho("  crontab -e", fg="cyan")
    typer.echo("\nand paste in the above line, save and exit.\n")
