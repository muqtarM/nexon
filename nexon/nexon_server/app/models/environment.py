from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.models import Base


class Environment(Base):
    __tablename__ = "environments"

    name = Column(String, primary_key=True, index=True)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # store the packages list as JSON
    packages = Column(JSON,
                      nullable=False,
                      server_default="[]")
