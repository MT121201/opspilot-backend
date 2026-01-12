from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db

router = APIRouter()

@router.get("/db/ping")
async def ping(db: AsyncSession = Depends(get_db)):
	await db.execute(text("SELECT 1"))
	return {"db":"ok"}