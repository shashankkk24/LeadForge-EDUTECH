"""
LeadForge EDU Backend - Main FastAPI Application.

A production-grade EdTech sales lead automation platform.
Scrapes, scores, and generates personalized outreach for school leads.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from config import get_settings
from database import init_db, close_db
from routers import leads, outreach, scraper
from websocket.manager import WebSocketManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

settings = get_settings()
ws_manager = WebSocketManager()


# ============ LIFESPAN MANAGEMENT ============


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage app startup and shutdown.
    Initializes database and cleans up connections.
    """
    # Startup
    logger.info("Starting LeadForge EDU Backend...")
    try:
        await init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")

    yield

    # Shutdown
    logger.info("Shutting down LeadForge EDU Backend...")
    try:
        await close_db()
        logger.info("Database connection closed")
    except Exception as e:
        logger.error(f"Database shutdown error: {e}")


# ============ FASTAPI APP ============


app = FastAPI(
    title=settings.APP_NAME,
    description="AI-Powered EdTech Lead Pipeline",
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============ HEALTH CHECK ============


@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "websocket_connections": ws_manager.get_connection_count(),
    }


@app.get("/", tags=["root"])
async def root():
    """Root endpoint with API documentation."""
    return {
        "message": "LeadForge EDU API",
        "docs": "/docs",
        "redoc": "/redoc",
        "version": settings.APP_VERSION,
    }


# ============ WEBSOCKET ============


@app.websocket("/ws/leads")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket endpoint for real-time lead updates (Feature 6).

    Clients receive:
    - new_lead: When a new lead is scraped
    - job_status: When scrape job status changes
    """
    await ws_manager.connect(websocket)
    logger.info(f"New WebSocket connection. Total: {ws_manager.get_connection_count()}")

    try:
        while True:
            # Listen for client messages (optional keep-alive)
            data = await websocket.receive_text()
            logger.debug(f"WebSocket message: {data}")

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected. Total: {ws_manager.get_connection_count()}")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        ws_manager.disconnect(websocket)


# ============ INCLUDE ROUTERS ============


app.include_router(leads.router)
app.include_router(scraper.router)
app.include_router(outreach.router)


# ============ ERROR HANDLERS ============


@app.exception_handler(ValueError)
async def value_error_handler(request, exc):
    """Handle ValueError exceptions."""
    logger.error(f"ValueError: {exc}")
    return JSONResponse(
        status_code=400,
        content={"detail": str(exc)},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Handle unexpected exceptions."""
    logger.error(f"Unexpected error: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"},
    )


# ============ DEBUGGING ============


if __name__ == "__main__":
    import uvicorn

    logger.info("Starting development server...")
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.DEBUG,
        log_level="info",
    )
