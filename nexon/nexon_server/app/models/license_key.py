from sqlalchemy import Column, String, DateTime, JSON, Boolean
from sqlalchemy.sql import func
from app.models import Base


class LicenseKey(Base):
    __tablename__ = "license_keys"

    key             = Column(String, primary_key=True, index=True)
    studio          = Column(String, nullable=False, index=True)
    tier            = Column(String, nullable=False)        # free, pro, enterprise
    quotas          = Column(JSON, nullable=False)          # e.g. {"envs": 5, "builds": 100}
    used            = Column(JSON, nullable=False, default={})
    created_at      = Column(DateTime(timezone=True), server_default=func.now())
    expires_at      = Column(DateTime(timezone=True), nullable=True)
    is_active       = Column(Boolean, default=True, nullable=False)
