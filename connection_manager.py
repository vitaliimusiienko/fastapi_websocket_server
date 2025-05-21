from fastapi import WebSocket

class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            
    async def send_message(self, message: str):
        for connection in self.active_connections:
            try:
                connection.send_text(message)
            except Exception as e:
                print(f"Error sending message: {e}")
                self.disconnect(connection)

    def count_connections(self):
        return len(self.active_connections)