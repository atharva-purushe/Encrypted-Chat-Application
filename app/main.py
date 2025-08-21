import logging
from typing import Optional, List
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Depends, Query, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

from .db import Base, engine, get_db
from .auth import router as auth_router, verify_token
from .ws_manager import ConnectionManager
from .crypto import encrypt_text, decrypt_text
from .models import Message
from .schemas import MessageResponse

# ✅ Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="🔐 Encrypted Chat Application",
    description="A secure, real-time chat platform built with FastAPI, WebSockets, and encrypted persistence.",
    version="1.0.0",
)

# ✅ Create tables (users, messages)
Base.metadata.create_all(bind=engine)

# ✅ Include auth routes
app.include_router(auth_router)

# ✅ Mount static files (for client.html and favicon.ico)
app.mount("/static", StaticFiles(directory="static"), name="static")

manager = ConnectionManager()


@app.get("/", summary="Root Endpoint")
def root():
    """Redirect root to the web client"""
    return RedirectResponse(url="/client")


@app.get(
    "/client",
    response_class=HTMLResponse,
    summary="Open the web chat client",
    description="Serves a minimal HTML/JS client for connecting to chat rooms over WebSockets.",
)
def client_html():
    with open("static/client.html", "r", encoding="utf-8") as f:
        return HTMLResponse(f.read())


@app.websocket("/ws/{room}")
async def websocket_endpoint(
    websocket: WebSocket,
    room: str,
    token: Optional[str] = Query(None, description="JWT access token"),
    db: Session = Depends(get_db),
):
    """
    WebSocket endpoint for real-time chat.
    - Requires a valid JWT token.
    - Messages are encrypted before being stored in the database.
    - Plaintext is broadcast in real-time to connected clients.
    """
    if not token:
        await websocket.close(code=4401)
        return

    try:
        payload = verify_token(token)
        username = payload.get("sub")
        if not username:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except Exception:
        await websocket.close(code=4401)
        return

    await manager.connect(room, websocket)
    logger.info(f"🔌 {username} connected to room '{room}'")
    await manager.broadcast(room, f"[system] {username} joined '{room}'")

    try:
        while True:
            text = await websocket.receive_text()

            # Encrypt + save
            ciphertext = encrypt_text(text)
            msg = Message(room=room, sender=username, content_ciphertext=ciphertext)
            db.add(msg)
            db.commit()
            db.refresh(msg)

            logger.info(f"💬 {username} -> room '{room}': {text}")

            # Broadcast plaintext
            await manager.broadcast(room, f"{username}: {text}")

    except WebSocketDisconnect:
        manager.disconnect(room, websocket)
        logger.info(f"❎ {username} disconnected from room '{room}'")
        await manager.broadcast(room, f"[system] {username} left '{room}'")


@app.get(
    "/rooms/{room}/history",
    response_model=List[MessageResponse],
    summary="Get chat history for a room",
    description="Fetches the **most recent decrypted messages** from the database for a given room. Requires a valid JWT token.",
)
def get_room_history(
    room: str,
    token: str = Query(..., description="JWT access token from /auth/login or /auth/register"),
    limit: int = 50,
    db: Session = Depends(get_db),
):
    _ = verify_token(token)

    rows: list[Message] = (
        db.query(Message)
        .filter(Message.room == room)
        .order_by(Message.id.desc())
        .limit(min(limit, 200))
        .all()
    )

    logger.info(f"📜 Chat history requested for room '{room}' (limit={limit})")

    items: list[MessageResponse] = []
    for r in reversed(rows):
        items.append(
            MessageResponse(
                id=r.id,
                room=r.room,
                sender=r.sender,
                content=decrypt_text(r.content_ciphertext),
                created_at=r.created_at,
            )
        )
    return items
