from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func

from app.models import Base


class AuditEntry(Base):
    __tablename__ = "audit"

    id        = Column(Integer,
                       primary_key=True,
                       autoincrement=True)
    timestamp = Column(DateTime(timezone=True),
                       server_default=func.now(),
                       nullable=False,
                       index=True)
    user      = Column(String,  nullable=False, index=True)
    action    = Column(String,  nullable=False, index=True)
    target    = Column(String,  nullable=False)
    details   = Column(Text,    nullable=True)
