# try:
#     # Pydantic v1 or v2+ with extras
#     from pydantic import BaseSettings
# except ImportError:
    # Pydantic v2 minimal install
from pydantic_settings import BaseSettings

from typing import Optional
from pydantic import Field


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


settings = Settings()
