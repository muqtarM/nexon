import getpass
from pathlib import Path
import yaml

from nexon_cli.utils.paths import *
from nexon_cli.utils.logger import logger


class AuthError(Exception):
    """Raised when a user isn't allowed to perform an action"""


class AuthManager:
    """
    Simple RBAC: loads user->role mappings from ~/.nexon/roles.yaml
    and enforces action->allowed_roles defined here.
    """

    # Map internal action names -> list of roles allowed
    _PERMISSIONS = {
        "activate_env":         ["admin", "dev"],
        "create_env":           ["admin", "dev"],
        "delete_env":           ["admin"],
        "install_package":      ["admin", "dev"],
        "uninstall_package":    ["admin", "dev"],
        "create_package":       ["admin"],
        "build_package":        ["admin", "dev"],
        "build_docker":         ["admin", "dev"],
        "apply_recipe":         ["admin", "dev"],
        # ... add more as you go ...
    }

    def __init__(self):
        self.roles_file: Path = Path(BASE_DIR) / "roles.yaml"
        self._user_roles = self._load_roles()

    def _load_roles(self) -> dict:
        if not self.roles_file.exists():
            logger.warning(f"No roles file at {self.roles_file}; defaulting everyone to 'dev'")
            return {}
        with open(self.roles_file, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
        return data.get("users", {})

    def current_user(self) -> str:
        return getpass.getuser()

    def current_role(self) -> str:
        user = self.current_user()
        return self._user_roles.get(user, "dev")

    def check(self, action: str):
        """
        Raise AuthError if the current user's role is not in the allowlist.
        """
        role = self.current_role()
        allowed = self._PERMISSIONS.get(action, [])
        if role not in allowed:
            msg = f"User '{self.current_user()}' (role: {role}) not permitted to perform '{action}'."
            logger.error(msg)
            raise AuthError(msg)
        # else: permitted
