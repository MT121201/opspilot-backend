# app/api/v1/api.py
from fastapi import APIRouter

from app.api.v1.endpoints import db_debug

api_router = APIRouter()
api_router.include_router(db_debug.router, tags=["debug"])