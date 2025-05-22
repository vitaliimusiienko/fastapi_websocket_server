import asyncio 
import signal
import logging
import os
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from connection_manager import ConnectionManager
from shutdown_handler import ShutdownHandler

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()
manager = ConnectionManager()
minutes_to_shutdown = 30
shutdown_handler = ShutdownHandler(manager, timeout_minutes=minutes_to_shutdown)
test_message = "Test notification"
background_tasks = []

def signal_shutdown_handler(signum, frame):
    shutdown_handler.handle_signal(signum, frame)

@app.on_event("startup")
async def startup_event():
    # signal work only in the main thread, and with 1 worker
    signal.signal(signal.SIGINT, signal_shutdown_handler)
    signal.signal(signal.SIGTERM, signal_shutdown_handler)

    background_tasks.append(asyncio.create_task(shutdown_handler.wait_for_shutdown(on_shutdown)))
    background_tasks.append(asyncio.create_task(send_test_notification()))
    logger.info("Server started and waiting for shutdown signal...")

async def send_test_notification():
    while not shutdown_handler.shutdown_event.is_set():
        await asyncio.sleep(10) # Wait for 10 seconds before sending the message
        count = manager.count_connections()

        if count > 0:
            await manager.send_message(test_message)
            logger.info(f"Sent message to {count} clients.")

        else:
            logger.info("No active connections to send message to")         
        await asyncio.sleep(5)

async def on_shutdown():
    logger.info("Shutting down server...")

    for task in background_tasks:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    os.kill(os.getpid(), signal.SIGTERM)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)

    try:
        while True:
            data = await websocket.receive_text()
            logger.info(f"Received message from client: {data}")
            await manager.send_message(data)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        if manager.count_connections() == 0:
            shutdown_handler.handle_signal(signal.SIGTERM, None)
        
        
        
        
    except Exception as e:
        logger.error(f"Error: {e}")
        manager.disconnect(websocket)
        await websocket.close()