import os
import subprocess
import tarfile
from pathlib import Path
from datetime import datetime

from nexon_cli.core.configs import config
from nexon_cli.utils.logger import logger


class BackupError(Exception):
    pass


class BackupManager:
    """
    Handles DB + filesystem backups and restores
    """

    def __init__(self):
        # Where to store local backups
        self.backup_dir = Path(config.base_dir) / "backups"
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # DB connection string (e.g. for Postgres)
        self.db_url = os.environ.get("DATABASE_URL")

        # What to back up on disk (env, packages, layers, etc.)
        self.paths = {
            "envs": Path(config.environments_dir),
            "pkgs": Path(config.packages_dir),
            "layers": Path(config.layers_dir),
            # include recipies, plugins, audit.log etc.
            "recipes": Path(config.recipes_dir),
            "audit": Path(config.base_dir) / "audit.log"
        }

    def backup_all(self) -> Path:
        """
        Dump the database and tar up all relevant directories into a timestamped archive.
        Returns path to the backup file.
        """
        timestamp = datetime.utcnow().strftime("%Y%m%d%T%H%M%SZ")
        archive = self.backup_dir / f"nexon_backup_{timestamp}.tar.gz"

        # 1) Database dump
        db_dump = self.backup_dir / f"db_{timestamp}.sql"
        if not self.db_url:
            raise BackupError("DATABASE_URL not set, cannot dump database")
        try:
            subprocess.run(
                ["pg_dump", self.db_url, "-f", str(db_dump)],
                check=True
            )
            logger.info(f"Database dumped to {db_dump}")
        except Exception as e:
            raise BackupError(f"DB dump failed: {e}")

        # 2) Tar all paths + the SQL dump
        with tarfile.open(archive, "w:gz") as tar:
            tar.add(db_dump, arcname=db_dump.name)
            for name, p in self.paths.items():
                if p.exists():
                    tar.add(p, arcname=name)
            logger.info(f"Added {len(self.paths)} paths to archive")
        logger.success(f"Backup created: {archive}")

        # 3) Clean up intermediate dump
        db_dump.unlink(missing_ok=True)
        return archive

    def list_backups(self) -> list[Path]:
        """List existing backup archives sorted by modified time descending."""
        return sorted(self.backup_dir.glob("nexon_backup_*.tar.gz"),
                      key=lambda p: p.stat().st_mtime,
                      reverse=True)

    def restore(self, archive_path: str) -> None:
        """
                Restore from the given backup archive:
                  - Re-import the SQL dump
                  - Overwrite the on-disk directories
                """
        arch = Path(archive_path)
        if not arch.exists():
            raise BackupError(f"Archive not found: {arch}")
        with tarfile.open(arch, "r:gz") as tar:
            members = tar.getmembers()
            # Extract SQL first
            sqls = [m for m in members if m.name.startswith("db_") and m.name.endswith(".sql")]
            if not sqls:
                raise BackupError("No DB dump found in archive")
            sql_member = sqls[0]
            dump_path = self.backup_dir / sql_member.name
            tar.extract(sql_member, path=self.backup_dir)
            # 1) Restore DB
            try:
                subprocess.run(
                    ["psql", self.db_url, "-f", str(dump_path)],
                    check=True
                )
                logger.info(f"Database restored from {dump_path}")
            except Exception as e:
                raise BackupError(f"DB restore failed: {e}")
            # 2) Extract the rest of the directories (overwrite)
            for m in members:
                if m.name == sql_member.name:
                    continue
                tar.extract(m, path=config.base_dir)
            logger.success(f"Restored files from archive {arch}")
            # Clean up SQL dump
            dump_path.unlink(missing_ok=True)
