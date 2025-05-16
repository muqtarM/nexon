from fastapi import APIRouter, WebSocket, Depends
from app.core.notification_manager import notification_manager
from app.core.rbac import requires_permission
from app.routers.auth import get_current_user

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.websocket("/ws")
async def websocket_notifications(
        ws: WebSocket,
        current_user=Depends(get_current_user)      # enforce auth
):
    """
    Websocket endpoint clients connect to for real-time toasts.
    """
    await notification_manager.connect(ws)
    # keep connection open
    while True:
        try:
            await ws.receive_text()
        except Exception:
            break


@router.post("/send", dependencies=[Depends(requires_permission("notify:send"))])
def http_notify(payload: dict, current_user=Depends(get_current_user)):
    """
    Accept JSON {title, message, level} and broadcast/
    """
    notification_manager.notify(
        title=payload["title"],
        message=payload["message"],
        level=payload.get("level", "info")
    )
    return {"status": "ok"}
