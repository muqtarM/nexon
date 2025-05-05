from fastapi import APIRouter, Depends, Response
from prometheus_client import CollectorRegistry, Gauge, generate_latest
from prometheus_client.exposition import CONTENT_TYPE_LATEST
from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models.environment import Environment
from app.models.package import Package
from app.models.audit import AuditEntry

router = APIRouter(prefix="/metrics", tags=["metrics"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/")
def metrics(db: Session = Depends(get_db)):
    """
    Expose basic Prometheus metrics for environments, packages, audits
    """
    registry = CollectorRegistry()
    # Gauges for entity counts
    env_gauge = Gauge(
        'nexon_environments_total',
        'Total number of environments',
        registry=registry
    )
    pkg_gauge = Gauge(
        'nexon_packages_total',
        'Total number of packages',
        registry=registry
    )
    audit_gauge = Gauge(
        'nexon_audit_entries_total',
        'Total number of audit log entries',
        registry=registry
    )

    # Set gauge values from the database
    env_gauge.set(db.query(Environment).count())
    pkg_gauge.set(db.query(Package).count())
    audit_gauge.set(db.query(AuditEntry).count())

    # Generate Prometheus text format
    data = generate_latest(registry)
    return Response(content=data, media_type=CONTENT_TYPE_LATEST)
