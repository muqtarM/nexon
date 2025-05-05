from sqlalchemy.ext.declarative import declarative_base

# single Base for all models
Base = declarative_base()

# import your models so that Base.metadata is populated
# e.g.:
from app.models.user import User
from app.models.environment import Environment
from app.models.package import Package
from app.models.audit import AuditEntry
