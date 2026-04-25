"""LeadForge EDU — FastAPI Backend."""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from database import init_db, close_db
from routers import leads, outreach, scraper
from socket_manager import ws_manager   # singleton

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(name)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting LeadForge EDU…")
    try:
        await init_db()
        logger.info("Database ready")
    except Exception as e:
        logger.error(f"DB init failed: {e}")
    yield
    await close_db()


app = FastAPI(title="LeadForge EDU API", version="1.0.0", lifespan=lifespan)

# ── CORS — allow all origins so browser never gets blocked ───────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,          # must be False when allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ───────────────────────────────────────────────────────────────────
app.include_router(leads.router)
app.include_router(outreach.router)
app.include_router(scraper.router)


# ── WebSocket ─────────────────────────────────────────────────────────────────
@app.websocket("/ws/leads")
async def websocket_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()   # keep-alive; ignore content
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
    except Exception:
        ws_manager.disconnect(websocket)


# ── Health ────────────────────────────────────────────────────────────────────
@app.get("/health")
async def health():
    return {"status": "ok", "ws_connections": ws_manager.get_connection_count()}

@app.get("/")
async def root():
    return {"message": "LeadForge EDU API", "docs": "/docs"}
