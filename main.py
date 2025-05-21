import asyncio 
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse
from connection_manager import ConnectionManager

app = FastAPI()
manager = ConnectionManager()

message = "Test"

@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_test_notification())

async def send_test_notification():
    while True:
        await asyncio.sleep(10)
        await manager.send_message(message)

@app.post("/notification")
async def manual_notification():
        await manager.send_message(message)
        return JSONResponse(content={"message": "Notification sent"})

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            print(f"Message received: {data}")
            await manager.send_message(data)
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        print("Client disconnected")
    except Exception as e:
        print(f"Error: {e}")
        manager.disconnect(websocket)
        await websocket.close()
        