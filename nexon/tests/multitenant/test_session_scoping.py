import pytest
from sqlalchemy import text
from nexon_server.app.db import SessionLocal
from nexon_server.app.core.tenant_manager import TenantManager


@pytest.fixture(autouse=True)
def init_db(monkeypatch, tmp_path):
    # use sqlite file per test
    db_path = tmp_path / "tenant.db"
    monkeypatch.setenv("DATABASE_URL", f"sqlite:///{db_path}")
    from alembic import command
    from alembic.config import Config
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")
    yield


def test_scoped_session(monkeypatch):
    # Set tenant A and open a session
    TenantManager.set_tenant("A")
    dbA = SessionLocal()
    # insert a row into a tenant-scoped table
    dbA.execute(text("INSERT INTO environments (name, role, tenant_id) VALUES ('eA', 'dev', 'A')"))
    dbA.commit()

    # Switch to tenant B
    TenantManager.set_tenant("B")
    dbB = SessionLocal()
    # B should see no rows
    res = dbB.execute(text("SELECT count(*) FROM environments"))
    assert res.scalar() == 0

    # Back to A
    TenantManager.set_tenant("A")
    dbA2 = SessionLocal()
    res2 = dbA2.execute(text("SELECT count(*) FROM environments"))
    assert res2.scalar() == 1
