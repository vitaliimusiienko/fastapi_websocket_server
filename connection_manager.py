import logging
from fastapi import WebSocket
from typing import List
from shutdown_handler import ShutdownHandler
import signal

logger = logging.getLogger(__name__)
shutdown_handler = ShutdownHandler(manager=None, timeout_minutes=1)

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
        logger.info(f"Client connected: Total: {self.count_connections()}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"Client disconnected: Total: {self.count_connections()}")

    async def close_all_connections(self):
        for connection in self.active_connections:
            try:
                await connection.close()
                logger.info("Closed connection")
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
            self.active_connections.clear()
            logger.info("All connections closed")
            
    async def send_message(self, message: str):
        for connection in list(self.active_connections):
            try:
                await connection.send_text(message)
                logger.info(f"Message sent to client: {message}")
            except Exception as e:
                logger.error(f"Error sending message to client: {e}")

                try:
                    await connection.close()    
                except:
                    pass
                self.disconnect(connection)

    def count_connections(self):
        return len(self.active_connections)