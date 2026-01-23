from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

import jwt


class JWTError(Exception):
	pass


def create_access_token(*, subject: str,
                        serect_key: str,
                        algorithm: str,
                        expire_minutes: int,
                        claims: dict[str, Any],
                        ) -> str:
	now = datetime.now(UTC)
	payload = {
		"sub": subject,
		"iat": int(now.timestamp()),
		"exp": int((now + timedelta(minutes=expire_minutes)).timestamp()),
		**claims,
	}
	return jwt.encode(payload, serect_key, algorithm=algorithm)


def decode_access_token(*, token: str, serect_key: str, algorithm: str) -> dict[str, Any]:
	try:
		return jwt.decode(token, serect_key, algorithms=[algorithm])
	except jwt.ExpiredSignatureError as e:
		raise JWTError("Token expired") from e
	except jwt.InvalidTokenError as e:
		raise JWTError("Invalid token") from e