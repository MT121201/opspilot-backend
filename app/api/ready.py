# app/api/ready.py
from fastapi import APIRouter, Request, status
from fastapi.responses import JSONResponse

from sqlalchemy import text

router = APIRouter()
@router.get("/ready")
async def ready(request: Request):
	engine = getattr(request.app.state, "db_engine", None)
	if engine is None:
		return JSONResponse(
			{"status":"not_ready", "db":"not_initialized"},
			status_code=status.HTTP_503_SERVICE_UNAVAILABLE)
	try:
		async with engine.connect() as conn:
			await conn.execute(text("SELECT 1"))
		return JSONResponse({"status":"ready", "db":"ok"})
	except Exception:
		return JSONResponse({"status":"not_ready", "db":"error"}, status_code=status.HTTP_503_SERVICE_UNAVAILABLE)