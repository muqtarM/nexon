from sqlalchemy import Column, String, Text, DateTime
from sqlalchemy.sql import func
from app.models import Base


class PluginSubmission(Base):
    __tablename__ = "plugin_submissions"
    id = Column(String, primary_key=True)   # uuid
    name = Column(String, nullable=False)
    repo_url = Column(String, nullable=False)
    author = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, approved, rejected
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    reviewer = Column(String, nullable=True)
