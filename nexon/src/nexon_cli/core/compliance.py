import os, functools
from cryptography.fernet import Fernet

# load a local-only flag
TPN_MODE = os.getenv("TPN_MODE", "false").lower() == "true"
KEY = os.getenv("TPN_KEY")  # base64 Fernet key


def tpn_valve(func):
    """Decorator to block network calls when in TPN_MODE."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if TPN_MODE and func.__module__.startswith("requests"):
            raise RuntimeError("Network calls forbidden in TPN mode")
        return func(*args, **kwargs)
    return wrapper


def encrypt_file(path: str):
    f = Fernet(KEY)
    data = open(path, "rb").read()
    open(path, "wb").write(f.encrypt(data ))
