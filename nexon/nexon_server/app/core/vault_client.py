import os
import hvac
from typing import Any


class VaultClientError(Exception):
    pass


class VaultClient:
    """
    Wraps HashiCorp Vault KV v2 to fetch secrets at startup.
    """

    def __init__(self):
        self.url = os.getenv("VAULT_ADDR")
        self.token = os.getenv("VAULT_TOKEN")
        if not (self.url and self.token):
            raise VaultClientError("VAULT_ADDR and VAULT_TOKEN must be set")
        self.client = hvac.Client(url=self.url, token=self.token)

    def get_secret(self, path: str, mount: str = "secret") -> dict[str, Any]:
        """
        Read kv v2 secret at "<mount>/data/<path>".
        """
        try:
            res = self.client.secrets.kv.v2.read_secret_version(
                path=path, mount_point=mount
            )
            return res["data"]["data"]
        except Exception as e:
            raise VaultClientError(f"Error reading secret {path}: {e}")
