import asyncio
from typing import List, Dict
from fastapi import WebSocket


class NotificationManager:
    """
    Holds active WebSocket connections and broadcasts notification events.
    """
    def __init__(self):
        self._clients: List[WebSocket] = []
        self._queue: asyncio.Queue[Dict] = asyncio.Queue()

        # background task for broadcasting
        asyncio.create_task(self._broadcaster())

    async def _broadcaster(self):
        while True:
            event = await self._queue.get()
            data = event.copy()
            for ws in list(self._clients):
                try:
                    await ws.send_json(data)
                except RuntimeError:
                    # client disconnected
                    self._clients.remove(ws)

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self._clients.append(websocket)

    def notify(self, title: str, message: str, level: str = "info"):
        """
        Enqueue a notification event to all connected clients.
        Levels: 'info', 'success', 'warning', 'error'
        """
        self._queue.put_nowait({
            "title": title,
            "message": message,
            "level": level,
            "timestamp": asyncio.get_event_loop().time()
        })


# singleton instance
notification_manager = NotificationManager()
