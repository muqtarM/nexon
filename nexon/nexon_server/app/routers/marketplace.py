from fastapi import APIRouter, Depends, HTTPException
from typing import List, Any, Dict, Optional
from pydantic import BaseModel

from app.core.marketplace import MarketplaceManager

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


class MarketplaceItemOut(BaseModel):
    name: str
    version: str
    description: Optional[str]
    metadata: Dict[str, Any]
    public: bool

    class Config:
        orm_mode = True


@router.get("/", response_model=List[MarketplaceItemOut])
def list_tools():
    mgr = MarketplaceManager()
    return mgr.list_items()


@router.get("/{name}/{version}", response_model=MarketplaceItemOut)
def get_tool(name: str, version: str):
    mgr = MarketplaceManager()
    item = mgr.get_item(name, version)
    if not item:
        raise HTTPException(404, "Not found")
    return item
