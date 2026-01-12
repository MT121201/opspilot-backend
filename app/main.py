# app/main.py
from __future__ import annotations

from functools import lru_cache
from contextlib import asynccontextmanager

from fastapi import FastAPI
from sqlalchemy import text

from app.api.health import router as health_router
from app.api.ready import router as ready_router
from app.api.v1.api import api_router
from app.core.config import Settings
from app.core.logging import setup_logging, get_logger

from app.db.session import create_engine, create_sessionmaker


@lru_cache()
def get_settings() -> Settings:
	return Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
	settings = get_settings()

	setup_logging(log_level=settings.LOG_LEVEL)
	logger = get_logger(__name__)

	# Store setting in app.state for use in other parts of the app
	app.state.settings = settings

	# DB
	engine = create_engine(settings.DATABASE_URL)
	session_maker = create_sessionmaker(engine)
	app.state.db_engine = engine
	app.state.db_session_maker = session_maker

	try:
		async with engine.connect() as conn:
			await conn.execute(text("SELECT 1"))
		logger.info("Database connection successful")
	except Exception:
		# Do not crash dev startup; health endpoint will show 503
		logger.error("DB connection FAILED at startup")

	logger.info("Starting server", extra={"app_name": settings.APP_NAME})
	try:
		yield
	finally:
		logger.info("Stopping server", extra={"app_name": settings.APP_NAME})
		await engine.dispose()

def create_app() -> FastAPI:
	app = FastAPI(lifespan=lifespan ,title="OpsPilot Backend", version="0.1.0")
	app.include_router(health_router)
	app.include_router(ready_router)
	app.include_router(api_router, prefix="/v1")
	return app

app = create_app()