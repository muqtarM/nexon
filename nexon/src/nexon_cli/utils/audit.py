import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime

from nexon_cli.utils.paths import *

# Ensure audit directory exits
audit_dir = Path(BASE_DIR)
audit_dir.mkdir(parents=True, exist_ok=True)

# Set up logger
audit_logger = logging.getLogger("nexon_audit")
audit_logger.setLevel(logging.INFO)
handler = RotatingFileHandler(
    audit_dir / "audit.log",
    maxBytes=5*1024*1024,
    backupCount=3,
    encoding="utf-8"
)
formatter = logging.Formatter("%(asctime)s | %(message)s", "%Y-%m-%dT%H:%M:%S")
handler.setFormatter(formatter)
audit_logger.addHandler(handler)


def log(action: str, user: str, target: str, details: str = ""):
    """
    Write a single audit entry.
    Format: TIMESTAMP | USER | ACTION | TARGET | DETAILS
    """
    entry = f"{user} | {action} | {target}"
    if details:
        entry += f" | {details}"
    audit_logger.info(entry)
