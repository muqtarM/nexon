from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

from app.config import settings
from app.core.tenant_manager import TenantManager

# Global engine (could be per-tenant URL if using separate DBs)
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)

# Use scoped_session to tie SQLAlchemy sessions to contextvars
SessionLocal = scoped_session(
    sessionmaker(bind=engine, autoflush=False, autocommit=False),
    scopefunc=lambda: TenantManager.get_tenant()
)


def get_db():
    """
    FastAPI dependency: yields a DB session scoped to the current tenant.
    """
    db = SessionLocal()
    try:
        # If using RLS (Postgres), set the tenant is session:
        db.execute(f"SET app.tenant = '{TenantManager.get_tenant()}';")
        yield db
    finally:
        db.close()
