from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from app.db import SessionLocal
from app.models.audit import AuditEntry
from app.schemas.audit import AuditEntryOut
from app.routers.auth import get_current_user

router = APIRouter(prefix="/audit", tags=["audit"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/", response_model=List[AuditEntryOut])
def list_audit(
        limit: int = 100,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    return db.query(AuditEntry).order_by(AuditEntry.timestamp.desc()).limit(limit).all()
