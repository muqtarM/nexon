from fastapi import APIRouter, Depends, HTTPException
from typing import List
from pydantic import BaseModel
from app.core.developer_portal import PortalManager, DeveloperPortalError
from app.core.rbac import requires_permission
from app.routers.auth import get_current_user

router = APIRouter(prefix="/developer", tags=["developer"])


class SubmissionIn(BaseModel):
    name: str
    repo_url: str
    author: str
    description: str | None = None


class SubmissionOut(BaseModel):
    id: str
    name: str
    repo_url: str
    author: str
    description: str | None
    status: str
    created_at: str
    reviewed_at: str | None
    reviewer: str | None


@router.post(
    "/plugins", response_model=SubmissionOut,
    dependencies=[Depends(requires_permission("devportal:submit"))]
)
def submit_plugin(payload: SubmissionIn):
    try:
        pm = PortalManager()
        return pm.submit_plugin(
            payload.name, payload.repo_url,
            payload.author, payload.description
        )
    except DeveloperPortalError as e:
        raise HTTPException(400, str(e))


@router.get(
    "/plugins", response_model=List[SubmissionOut],
    dependencies=[Depends(requires_permission("devportal:review"))]
)
def list_submissions():
    return PortalManager().list_submissions()


@router.post(
    "/plugins/{pid}/review",
    response_model=SubmissionOut,
    dependencies=[Depends(requires_permission("devportal:review"))]
)
def review_plugin(pid: str, approve: bool, current_user=Depends(get_current_user)):
    try:
        return PortalManager().review(pid, approve, current_user["username"])
    except DeveloperPortalError as e:
        raise HTTPException(404, str(e))
