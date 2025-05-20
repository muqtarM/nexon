# try:
#     # Pydantic v1 or v2+ with extras
#     from pydantic import BaseSettings
# except ImportError:
    # Pydantic v2 minimal install
from pydantic_settings import BaseSettings

from typing import Optional
from app.core.vault_client import VaultClient, VaultClientError


class Settings(BaseSettings):
    # existing...
    SHOTGRID_URL:       Optional[str] = None
    SHOTGRID_SCRIPT:    Optional[str] = None
    SHOTGRID_KEY:       Optional[str] = None

    P4_PORT:            Optional[str] = None
    P4_USER:            Optional[str] = None
    P4_CLIENT:          Optional[str] = None

    VERSION: str = "0.1.0"

    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    LDAP_URL: Optional[str] = None
    LDAP_BASE_DN: Optional[str] = None

    class Config:
        env_file = ".env"
        case_sensitive = True


def load_settings() -> Settings:
    # 1) Load initial from .env / envvars
    settings = Settings()
    # 2) Optionally overlay Vault secrets
    try:
        vc = VaultClient()
        for key, val in vc.get_secret("nexon/app").items():
            setattr(settings, key, val)
    except VaultClientError:
        # no Vault integration in lower envs
        pass
    return settings


settings = load_settings()
