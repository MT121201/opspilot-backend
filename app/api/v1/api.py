# app/api/v1/api.py
from fastapi import APIRouter

from app.api.v1.endpoints import auth, db_debug, documents, tickets, users

api_router = APIRouter()
api_router.include_router(db_debug.router, tags=["debug"])
api_router.include_router(users.router, tags=["users"])
api_router.include_router(tickets.router, tags=["tickets"])
api_router.include_router(auth.router, tags=["auth"])
api_router.include_router(documents.router, tags=["documents"])