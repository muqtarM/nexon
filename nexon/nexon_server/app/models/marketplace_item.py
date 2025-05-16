from sqlalchemy import Column, String, Text, JSON, Boolean
from app.models import Base


class MarketplaceItem(Base):
    __tablename__ = "marketplace_items"
    name          = Column(String, primary_key=True)
    version       = Column(String, primary_key=True)
    description   = Column(Text, nullable=True)
    metadata      = Column(JSON, nullable=False)    # e.g. install commands, tags
    public        = Column(Boolean, default=False)
