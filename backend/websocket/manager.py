"""
WebSocket manager for real-time lead updates (Feature 6: WebSocket Live Feed).
Handles connection management and broadcasting new leads to connected clients.
"""

import json
import logging
from typing import Set

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class WebSocketManager:
    """Manages WebSocket connections and broadcasts."""

    def __init__(self):
        """Initialize WebSocket manager with empty connections set."""
        self.active_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket):
        """
        Accept WebSocket connection and add to active connections.

        Args:
            websocket: WebSocket connection to accept
        """
        await websocket.accept()
        self.active_connections.add(websocket)
        logger.info(f"WebSocket connected. Total connections: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        """
        Remove connection from active set.

        Args:
            websocket: WebSocket connection to disconnect
        """
        self.active_connections.discard(websocket)
        logger.info(f"WebSocket disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast_new_lead(self, lead_data: dict):
        """
        Broadcast new lead to all connected clients.

        Args:
            lead_data: Lead dictionary to broadcast
        """
        if not self.active_connections:
            logger.debug("No WebSocket connections - skipping broadcast")
            return

        message = {
            "type": "new_lead",
            "data": lead_data,
        }

        # Send to all connected clients
        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error broadcasting to client: {e}")
                disconnected.add(connection)

        # Clean up disconnected clients
        for connection in disconnected:
            self.disconnect(connection)

        logger.debug(f"Broadcasted new lead to {len(self.active_connections)} clients")

    async def broadcast_job_status(self, job_id: str, status: str, leads_found: int = 0):
        """
        Broadcast scrape job status update.

        Args:
            job_id: Job ID
            status: Job status (pending, running, completed, failed)
            leads_found: Number of leads found
        """
        if not self.active_connections:
            return

        message = {
            "type": "job_status",
            "job_id": job_id,
            "status": status,
            "leads_found": leads_found,
        }

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error broadcasting job status: {e}")
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection)

    async def broadcast_message(self, message_type: str, data: dict):
        """
        Broadcast generic message to all clients.

        Args:
            message_type: Type of message
            data: Message data
        """
        if not self.active_connections:
            return

        message = {
            "type": message_type,
            "data": data,
        }

        disconnected = set()
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception as e:
                logger.warning(f"Error broadcasting message: {e}")
                disconnected.add(connection)

        for connection in disconnected:
            self.disconnect(connection)

    async def handle_client_message(self, websocket: WebSocket) -> dict:
        """
        Receive and parse client message.

        Args:
            websocket: WebSocket connection

        Returns:
            Parsed message dictionary
        """
        try:
            data = await websocket.receive_text()
            return json.loads(data)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON received from client")
            return {}
        except WebSocketDisconnect:
            self.disconnect(websocket)
            raise
        except Exception as e:
            logger.error(f"Error receiving message: {e}")
            return {}

    def get_connection_count(self) -> int:
        """Get number of active WebSocket connections."""
        return len(self.active_connections)
