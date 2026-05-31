import logging
from pathlib import Path

from fastapi import (
    HTTPException,
    Request,
    Response,
    status,
)

from bot.settings import settings as s
from bot.video.file_streaming import (
    build_full_response,
    build_range_response,
)

logger = logging.getLogger(__name__)

_MAX_VIDEO_SIZE = 500 * 1024 * 1024


def _validate_video_path(file_path: Path) -> Path:
    if not file_path.exists():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Video not found.")

    resolved = file_path.resolve()
    base_dir = Path(s.VIDEO_DATA_DIR).resolve()

    if not str(resolved).startswith(str(base_dir)):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Access denied.")

    if resolved.stat().st_size > _MAX_VIDEO_SIZE:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="File too large.")

    return resolved


def _parse_range(range_header: str, file_size: int) -> tuple[int, int]:
    if not range_header.startswith("bytes="):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid range format.")

    range_spec = range_header[6:]
    parts = range_spec.split("-", 1)
    if len(parts) != 2:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid range format.")

    try:
        if parts[0] == "":
            suffix_length = int(parts[1])
            start = max(0, file_size - suffix_length)
            end = file_size - 1
        elif parts[1] == "":
            start = int(parts[0])
            end = file_size - 1
        else:
            start = int(parts[0])
            end = int(parts[1])
    except (ValueError, TypeError) as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid range values.") from exc

    if start < 0 or start >= file_size or end < start or end >= file_size:
        raise HTTPException(status_code=status.HTTP_416_REQUESTED_RANGE_NOT_SATISFIABLE, detail="Range not satisfiable.")

    return start, end


def stream_video(file_path: Path, request: Request) -> Response:
    resolved = _validate_video_path(file_path)
    file_size = resolved.stat().st_size

    range_header = request.headers.get("range")

    if range_header:
        start, end = _parse_range(range_header, file_size)
        return build_range_response(resolved, start, end, file_size)

    return build_full_response(resolved, file_size)


def serve_thumbnail(thumbnail_data: bytes) -> Response:
    if not thumbnail_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Thumbnail not available.")

    return Response(
        content=thumbnail_data,
        media_type="image/jpeg",
        headers={"Cache-Control": "private, max-age=86400"},
    )
