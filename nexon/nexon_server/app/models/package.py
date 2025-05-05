from sqlalchemy import Column, String, JSON, Text
from app.models import Base


class Package(Base):
    __tablename__ = "packages"

    name = Column(String, primary_key=True, index=True)
    version = Column(String, primary_key=True)
    description = Column(Text, nullable=True)
    # store the raw package.yaml contents (requires, env, commands)
    spec = Column(JSON, nullable=False, default="{}")
