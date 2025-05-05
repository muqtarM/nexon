from fastapi import APIRouter, Depends, HTTPException
from app.services.asset_tracker import ShotGridService, PerforceService, AssetTrackerError
from app.routers.auth import get_current_user

router = APIRouter(prefix="/assets", tags=["assets"])


@router.get("/shot/{shot_name}")
def get_shot(shot_name: str, current_user=Depends(get_current_user)):
    try:
        sg = ShotGridService()
        return sg.find_shot(shot_name)
    except AssetTrackerError as e:
        raise HTTPException(404, str(e))


@router.post("/p4/sync")
def p4_sync(
        depot_path: str,
        current_user=Depends(get_current_user)
):
    from app.config import settings
    try:
        p4 = PerforceService(settings.P4_PORT, settings.P4_USER, settings.P4_CLIENT)
        out = p4.sync(depot_path)
        return {"result": out}
    except AssetTrackerError as e:
        raise HTTPException(500, str(e))
