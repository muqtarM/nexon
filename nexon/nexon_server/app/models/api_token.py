from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.models import Base


class APIToken(Base):
    __tablename__ = "api_tokens"
    token       = Column(String, primary_key=True, index=True)
    user        = Column(String, nullable=False, index=True)
    scopes      = Column(JSON, nullable=False)          # e.g. ["env:create", "pkg:install"]
    description = Column(String, nullable=True)
    created_at  = Column(DateTime(timezone=True),
                         server_default=func.now(),
                         nullable=False)
    expires_at  = Column(DateTime(timezone=True), nullable=True)
