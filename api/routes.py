import os
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, FileResponse
from api.websocket import manager
from agent.orchestrator import orchestrator
from core.logger import logger

router = APIRouter()

# Path to index.html
WEB_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "web")
INDEX_PATH = os.path.join(WEB_DIR, "index.html")

@router.get("/", response_class=HTMLResponse)
async def get_index():
    """Serve the single page frontend HTML."""
    if os.path.exists(INDEX_PATH):
        return FileResponse(INDEX_PATH)
    return HTMLResponse("<h1>Ghost Pilot UI not found</h1>", status_code=404)

@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for voice-to-text input and real-time execution feedback."""
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_json()
            user_text = data.get("text", "").strip()

            if not user_text:
                continue

            logger.info(f"Received WS message: {user_text}")
            # Process command through LLM orchestrator and broadcast step progress
            await orchestrator.process_user_message(user_text, manager.broadcast)

    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info("Client disconnected from WebSocket.")
    except Exception as e:
        logger.error(f"WebSocket endpoint error: {e}", exc_info=True)
        manager.disconnect(websocket)
