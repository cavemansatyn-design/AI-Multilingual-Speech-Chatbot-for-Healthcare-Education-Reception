"""
Multilingual Speech-Based Chatbot — FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from database.db_connection import set_db_config
from api.routes_auth import router as auth_router
from api.routes_chat import router as chat_router
from api.routes_report import router as report_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize DB on startup; cleanup on shutdown."""
    settings = get_settings()
    set_db_config(settings.mongodb_uri, settings.mongodb_db_name)
    logger.info("Database configured: %s", settings.mongodb_db_name)
    yield
    # Optional: close MongoClient
    # get_mongo_client().close()


def create_app() -> FastAPI:
    app = FastAPI(
        title="Multilingual Speech Chatbot API",
        description="Speech/text chatbot with symptom screening, reports, translation, and TTS",
        version="1.0.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(auth_router, prefix="/auth", tags=["auth"])
    app.include_router(chat_router, prefix="/chat", tags=["chat"])
    app.include_router(report_router, prefix="/report", tags=["report"])
    return app


app = create_app()


@app.get("/")
def root():
    return {"service": "Multilingual Speech Chatbot", "docs": "/docs"}
