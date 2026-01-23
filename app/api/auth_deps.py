from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.config import Settings, get_settings
from app.core.jwt import JWTError, decode_access_token
from app.schemas.auth import UserContext
from app.services.user_service import UserNotFoundError, get_user_by_id


async def get_current_user(authorization: str | None = Header(default=None),
                           db: AsyncSession = Depends(get_db)) -> UserContext:
	if not authorization or not authorization.startswith("Bearer "):
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authorization header")

	token = authorization.removeprefix("Bearer ").strip()

	settings: Settings = get_settings()

	try:
		payload = decode_access_token(
			token=token,
			serect_key=settings.JWT_SECRET_KEY,
			algorithm=settings.JWT_ALGORITHM,
		)
	except JWTError as e:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)) from e

	user_id = payload.get("sub")
	if not user_id:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

	try:
		user = await get_user_by_id(db, user_id)
	except UserNotFoundError:
		raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")

	return UserContext(id=user.id, email=user.email, role=user.role)
