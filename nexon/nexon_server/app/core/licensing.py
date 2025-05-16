import uuid
from datetime import datetime, timedelta
from fastapi import HTTPException, status, Depends

from sqlalchemy.orm import Session
from app.db import SessionLocal
from app.models.license_key import LicenseKey
from app.routers.auth import get_current_user, oauth2_scheme


class LicensingError(Exception):
    pass


class LicensingManager:
    """
    Create, validate and meter license usage.
    """

    def __init__(self):
        self.db: Session = SessionLocal()

    def issue_key(self, studio: str, tier: str,
                  quotas: dict, valid_days: int | None = None) -> LicenseKey:
        key = str(uuid.uuid4())
        expires = datetime.utcnow() + timedelta(days=valid_days) if valid_days else None
        rec = LicenseKey(
            key=key, studio=studio, tier=tier,
            quotas=quotas, used={k: 0 for k in quotas},
            expires_at=expires
        )
        self.db.add(rec)
        self.db.commit()
        return rec

    def validate_key(self, key: str) -> LicenseKey:
        rec = self.db.query(LicenseKey).get(key)
        if not rec or not rec.is_active:
            raise LicensingError("Invalid or revoked license key")
        if rec.expires_at and rec.expires_at < datetime.utcnow():
            raise LicensingError("License expired")
        return rec

    def record_usage(self, key: str, feature: str, amount: int = 1):
        rec = self.validate_key(key)
        quota = rec.quotas.get(feature)
        used = rec.used.get(feature, 0)
        if quota is not None and used + amount > quota:
            raise LicensingError(f"Quota exceeded for '{feature}' ({used}/{quota})")
        rec.used[feature] = used + amount
        self.db.commit()
        return rec.used

    def revoke_key(self, key: str):
        rec = self.db.query(LicenseKey).get(key)
        if not rec:
            raise LicensingError("Key not found")
        rec.is_active = False
        self.db.commit()


def requires_license(feature: str):
    """
    Decorator to require a valid license and consume a unit of `feature`
    """
    def decorator(func):
        def wrapper(*args, license_key: str = Depends(oauth2_scheme), **kwargs):
            lm = LicensingManager()
            try:
                lm.record_usage(license_key, feature)
            except LicensingError as e:
                raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, str(e))
            return func(*args, **kwargs)
        return wrapper
    return decorator
