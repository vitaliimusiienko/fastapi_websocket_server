# fastapi_websocket_server

## Description

This project implements a WebSocket server using FastAPI that supports:

- Real-time notifications to all connected clients
- Tracking and management of active WebSocket connections
- Graceful shutdown mechanism:
  - Waits until all clients disconnect
  - Or forces shutdown after 30 minutes from receiving a termination signal

This implementation is intended for use as a test assignment for a Junior Python Developer position.

## Requirements

- Python 3.9+
- FastAPI
- Uvicorn

## Installation

1. Clone the repository or copy the project files.
2. Install dependencies using pip:

```bash
pip install -r requirements.txt
```

## Running the Server

Run the application using:

```bash
uvicorn main:app
```

**Note:** Signal-based graceful shutdown only works when using a single worker. Do not run with `--workers` greater than 1.

## WebSocket Endpoint

**URL:** `/ws`  
**Protocol:** WebSocket

Clients can connect to this endpoint to:

- Receive broadcast messages sent from the server
- Send messages to the server, which are then broadcast to all connected clients

### Example WebSocket Message Flow

1. Server sends a test notification every 10 seconds: `"Test notification"`
2. When a client sends a message, it is broadcast to all other connected clients.

## Graceful Shutdown Logic

Upon receiving a shutdown signal (`SIGINT` or `SIGTERM`), the server:

1. Starts monitoring active WebSocket connections
2. Waits until:
   - All clients disconnect, or
   - 30 minutes pass
3. Closes all remaining connections if timeout is reached
4. Logs shutdown progress (number of connections, remaining time)

**Important Implementation Details:**

- Signal handlers are registered at startup using Python’s `signal` module.
- Shutdown control is managed asynchronously via `asyncio.Event`.
- Background tasks are managed within the FastAPI lifecycle.

## Project Structure

```
.
├── main.py                # FastAPI application and signal handling
├── connection_manager.py # WebSocket connection manager
├── shutdown_handler.py   # Graceful shutdown logic
└── README.md              # Project documentation
```

## How to Test WebSocket

You can use tools such as:

### 1. Web browser console

```javascript
const socket = new WebSocket("ws://localhost:8000/ws");
socket.onmessage = (e) => console.log("Message from server:", e.data);
socket.send("Hello Server");
```

### 2. websocat (CLI tool)

```bash
websocat ws://localhost:8000/ws
```

## Coverage of Assignment Requirements

- [x] WebSocket server with `/ws` endpoint
- [x] Tracking and management of WebSocket clients
- [x] Broadcasting messages to all clients
- [x] Sending test notification every 10 seconds
- [x] Graceful shutdown with signal handling (`SIGINT`, `SIGTERM`)
- [x] Wait for all connections to close or force shutdown after 30 minutes
- [x] Logging of shutdown progress
- [x] Compatible with `uvicorn` using one worker

## Notes

- This implementation uses only built-in Python modules and FastAPI.
- Shutdown handling is designed for single-worker `uvicorn` mode.