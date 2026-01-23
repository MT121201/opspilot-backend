from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import Settings, get_settings
from app.core.jwt import create_access_token
from app.schemas.auth import LoginRequest, TokenResponse
from app.services.user_service import UserNotFoundError, get_user_by_email

router = APIRouter()

@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
	settings: Settings = get_settings()

	try:
		user = await get_user_by_email(db, str(payload.email))
	except UserNotFoundError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

	token = create_access_token(
		subject= str(user.id),
		serect_key=settings.JWT_SECRET_KEY,
		algorithm=settings.JWT_ALGORITHM,
		expire_minutes=settings.JWT_EXPIRES_MINUTES,
		claims={"role": user.role, "email": user.email}
	)

	return TokenResponse(access_token=token, token_type="bearer")

