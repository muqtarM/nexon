from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pydantic import BaseModel
from datetime import datetime

from app.routers.auth import get_current_user
from app.core.rbac import requires_permission
from app.core.token_manager import TokenManager

router = APIRouter(prefix="/auth/tokens", tags=["auth", "tokens"])


class TokenOut(BaseModel):
    token: str
    user: str
    scopes: List[str]
    description: str | None
    created_at: datetime
    expires_at: datetime | None


class TokenIn(BaseModel):
    scopes: List[str]
    description: str | None = None
    expired_in: int | None = None  # seconds


@router.post("/", response_model=TokenOut, dependencies=[Depends(requires_permission("auth:token:create"))])
def create_token(payload: TokenIn, current_user=Depends(get_current_user)):
    mgr = TokenManager()
    rec = mgr.create_token(
        user=current_user["username"],
        scopes=payload.scopes,
        description=payload.description,
        expires_in=payload.expired_in
    )
    return rec


@router.get("/", response_model=List[TokenOut], dependencies=[Depends(requires_permission("auth:token:read"))])
def list_tokens():
    mgr = TokenManager()
    return mgr.list_tokens()


@router.delete("/{token}", status_code=status.HTTP_204_NO_CONTENT,
               dependencies=[Depends(requires_permission("auth:token:revoke"))])
def revoke_token(token: str):
    mgr = TokenManager()
    if not mgr.revoke_token(token):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Token not found")
