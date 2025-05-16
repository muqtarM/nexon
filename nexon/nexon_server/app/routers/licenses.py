from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict
from app.core.licensing import LicensingManager, LicensingError
from app.core.rbac import requires_permission

router = APIRouter(prefix="/licenses", tags=["licensing"])


class IssueIn(BaseModel):
    studio: str
    tier: str
    quotas: Dict[str, int]
    valid_days: int | None = None


class IssueOut(BaseModel):
    key: str
    studio: str
    tier: str
    quotas: Dict[str, int]
    expires_at: str | None


@router.post("/", response_model=IssueOut, dependencies=[Depends(requires_permission("license:issue"))])
def issue_license(payload: IssueIn):
    mgr = LicensingManager()
    rec = mgr.issue_key(
        payload.studio, payload.tier,
        payload.quotas, payload.valid_days
    )
    return rec
