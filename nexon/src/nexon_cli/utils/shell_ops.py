import os
from typing import Dict

# Tracks only variables set by Nexon so they can be reset later
env_backup: Dict[str, str] = {}


def set_environment_variables(env_vars: Dict[str, str]):
    """
    Set environment variables for activation or build.
    Back up existing values so they can be reset
    :param env_vars:
    :return:
    """
    global env_backup
    for key, value in env_vars.items():
        # Backup old value (or None)
        if key not in env_backup:
            env_backup[key] = os.environ.get(key, None)
        # Set new value
        os.environ[key] = value


def reset_environment_variables():
    """
    Reset environment variables set by Nexon during deactivation.
    :return:
    """
    global env_backup
    for key, old_value in env_backup.items():
        if old_value is None:
            # Variable did not exist before
            os.environ.pop(key, None)
        else:
            os.environ[key] = old_value
    # Clear backup
    env_backup.clear()
