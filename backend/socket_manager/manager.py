"""WebSocket manager — singleton shared across the entire app."""

import logging
from typing import Set

from fastapi import WebSocket

logger = logging.getLogger(__name__)


class WebSocketManager:
    def __init__(self):
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WS connected. Total: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        self.active_connections.discard(websocket)
        logger.info(f"WS disconnected. Total: {len(self.active_connections)}")

    async def _broadcast(self, message: dict):
        if not self.active_connections:
            return
        dead = set()
        for ws in self.active_connections:
            try:
                await ws.send_json(message)
            except Exception:
                dead.add(ws)
        for ws in dead:
            self.disconnect(ws)

    async def broadcast_new_lead(self, lead_data: dict):
        await self._broadcast({"type": "NEW_LEAD", "data": lead_data})

    async def broadcast_job_status(self, job_id: str, status: str, leads_found: int = 0):
        type_map = {"running": "JOB_STARTED", "completed": "JOB_COMPLETED", "failed": "JOB_FAILED"}
        await self._broadcast({
            "type": type_map.get(status, "JOB_STATUS"),
            "job_id": job_id, "status": status, "leads_found": leads_found,
        })

    async def broadcast_message(self, message_type: str, data: dict):
        await self._broadcast({"type": message_type, "data": data})

    def get_connection_count(self) -> int:
        return len(self.active_connections)


# ── Single shared instance ────────────────────────────────────────────────────
ws_manager = WebSocketManager()
