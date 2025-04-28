import os

# Keep track of variables set by Nexon
NEXON_ENV_VARS = {}


def set_environment_variables(env_vars: dict):
    """
    Set environment variables for activation.
    :param env_vars:
    :return:
    """
    for key, value in env_vars.items():
        NEXON_ENV_VARS[key] = os.environ.get(key, None)  # Backup old value
        os.environ[key] = value


def reset_environment_variables():
    """
    Reset environment variables set by Nexon during deactivation.
    :return:
    """
    for key, old_value in NEXON_ENV_VARS.items():
        if old_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = old_value
    NEXON_ENV_VARS.clear()
