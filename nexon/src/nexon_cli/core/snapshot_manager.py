import subprocess
from pathlib import Path
from datetime import datetime

from nexon_cli.core.configs import config


class SnapshotManager:
    base = Path(config.base_dir) / "snapshots"

    def create(self, name: str = None):
        name = name or datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
        dest = self.base / name
        dest.mkdir(parents=True, exist_ok=True)
        # rsync with hard-linking to previous
        prev = sorted(self.base.iterdir())
        link_dest = prev[0] if prev else None
        cmd = ["rsync", "-aH", "--delete"]
        if link_dest:
            cmd += ["--link-dest", str(link_dest)]
        cmd += [config.base_dir, str(dest)]
        subprocess.run(cmd, check=True)
        return name

    def list(self):
        return [p.name for p in sorted(self.base.iterdir())]

    def restore(self, name: str):
        src = self.base / name
        if not src.exists():
            raise FileNotFoundError(name)
        subprocess.run(["rsync", "-aH", "--delete", str(src) + "/", config.base_dir], check=True)
