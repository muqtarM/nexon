import yaml
import requests
from nexon_cli.utils.logger import logger

# Load notification config once
cfg_path = None
try:
    from nexon_cli.core.configs import config
    cfg_path = config.base_dir / "notifications.yaml"
    _cfg = yaml.safe_load(open(cfg_path, "r")) or {}
except Exception:
    _cfg = {}


def _send(endpoint:str, payload: dict):
    try:
        resp = requests.post(endpoint, json=payload, timeout=5)
        resp.raise_for_status()
    except Exception as e:
        logger.error(f"[notify] Failed sending to {endpoint}: {e}")


def post_build_package(package: str, version: str, **_):
    ncfg = _cfg.get("slack", {})
    if "post_build_package" not in ncfg.get("hooks", []):
        return
    webhook = ncfg.get("webhook_url")
    channel = ncfg.get("channel", "")
    msg = {
        "text": f":hammer_and_wrench: Built *{package}-{version}*",
        "channel": channel,
    }
    _send(webhook, msg)


def post_install_package(env_name: str, added: list, **_):
    ncfg = _cfg.get("slack", {})
    if "post_install_package" not in ncfg.get("hooks", []):
        return
    webhook = ncfg.get("webhook_url")
    channel = ncfg.get("channel", "")
    pkg_list = ", ".join(added)
    msg = {
        "text": f":package: Installed into *{env_name}*: {pkg_list}",
        "channel": channel,
    }
    _send(webhook, msg)


def render_submit(env_name: str, scene_file: str, **_):
    ncfg = _cfg.get("teams", {})
    if "render_submit" not in ncfg.get("hooks", []):
        return
    webhook = ncfg.get("webhook_url")
    msg = {
        "text": f":rocket: Render submitted for *{env_name}* -> `{scene_file}`"
    }
    _send(webhook, msg)
