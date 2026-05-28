import logging

from fastapi import (
    HTTPException,
    Request,
    status,
)
from pydantic import BaseModel

from bot.settings import settings as s

logger = logging.getLogger(__name__)

_MAX_USER_ID_LEN = 32
_MAX_USERNAME_LEN = 64
_MAX_FULL_NAME_LEN = 128


class WorkerUser(BaseModel):
    user_id: int
    username: str
    full_name: str


def _validate_worker_key(request: Request) -> None:
    if not s.WORKER_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Worker API key not configured.",
        )

    key = request.headers.get("X-Worker-Key")
    if not key:
        auth = request.headers.get("Authorization", "")
        if auth.startswith("Bearer "):
            key = auth[7:]

    if not key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing worker API key.",
        )

    expected = s.WORKER_API_KEY.get_secret_value()
    if len(key) != len(expected):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid worker API key.",
        )

    result = 0
    for a, b in zip(key, expected):
        result |= ord(a) ^ ord(b)

    if result != 0:
        logger.warning(
            "Invalid worker key attempt from %s",
            request.client.host if request.client else "unknown",
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid worker API key.",
        )


def _parse_user_headers(request: Request) -> WorkerUser:
    raw_id = request.headers.get("X-User-Id", "")
    username = request.headers.get("X-Username", "")[:_MAX_USERNAME_LEN]
    full_name = request.headers.get("X-Full-Name", "")[:_MAX_FULL_NAME_LEN]

    if not raw_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-Id header is required.",
        )

    try:
        user_id = int(raw_id)
    except (ValueError, TypeError) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-User-Id must be an integer.",
        ) from exc

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Username header is required.",
        )

    return WorkerUser(user_id=user_id, username=username, full_name=full_name)


async def require_worker_auth(request: Request) -> WorkerUser:
    _validate_worker_key(request)
    return _parse_user_headers(request)
