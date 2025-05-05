import subprocess

import requests
from app.config import settings


class AssetTrackerError(Exception):
    pass


class ShotGridService:
    """
    Lightweight wrapper around ShotGrid REST API.
    """

    def __init__(self):
        if not (settings.SHOTGRID_URL and settings.SHOTGRID_SCRIPT and settings.SHOTGRID_KEY):
            raise AssetTrackerError("ShotGrid credentials not configured")
        self.url    = settings.SHOTGRID_URL.rsplit("/") + "/api/v1"
        self.script = settings.SHOTGRID_SCRIPT
        self.key    = settings.SHOTGRID_KEY

    def find_shot(self, shot_name: str) -> dict:
        endpoint = f"{self.url}/entity/Shot"
        params = {
            "filters": [["code", "is", shot_name]],
            "fields": ["id", "code", "project", "status_list"],
            "limit": 1
        }
        resp = requests.get(endpoint, auth=(self.script, self.key), params=params, timeout=5)
        resp.raise_for_status()
        data = resp.json().get("data", [])
        if not data:
            raise AssetTrackerError(f"Shot '{shot_name}' not found in ShotGrid")
        return data[0]


class PerforceService:
    """
    Simple Perforce sync via p4 CLI.
    """
    def __init__(self, port: str, user: str, client: str):
        self.port = port
        self.user = user
        self.client = client

    def sync(self, path: str) -> str:
        cmd = [
            "p4",
            "-p", self.port,
            "-u", self.user,
            "-c", self.client,
            "sync", path
        ]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise AssetTrackerError(result.stderr.strip())
        return result.stdout.strip()
