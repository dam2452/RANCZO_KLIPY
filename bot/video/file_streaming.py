from pathlib import Path

from fastapi import status
from fastapi.responses import StreamingResponse

_CHUNK_SIZE = 64 * 1024


def iter_file(file_path: Path, start: int, end: int):
    with open(file_path, "rb") as f:
        f.seek(start)
        remaining = end - start + 1
        while remaining > 0:
            chunk = f.read(min(_CHUNK_SIZE, remaining))
            if not chunk:
                break
            remaining -= len(chunk)
            yield chunk


def build_range_response(
    resolved: Path,
    start: int,
    end: int,
    file_size: int,
    content_type: str = "video/mp4",
    cache_control: str = "private, max-age=3600",
) -> StreamingResponse:
    return StreamingResponse(
        iter_file(resolved, start, end),
        status_code=status.HTTP_206_PARTIAL_CONTENT,
        headers={
            "Content-Range": f"bytes {start}-{end}/{file_size}",
            "Accept-Ranges": "bytes",
            "Content-Length": str(end - start + 1),
            "Content-Type": content_type,
            "Cache-Control": cache_control,
        },
    )


def build_full_response(
    resolved: Path,
    file_size: int,
    content_type: str = "video/mp4",
    cache_control: str = "private, max-age=3600",
) -> StreamingResponse:
    return StreamingResponse(
        iter_file(resolved, 0, file_size - 1),
        status_code=status.HTTP_200_OK,
        headers={
            "Content-Length": str(file_size),
            "Content-Type": content_type,
            "Accept-Ranges": "bytes",
            "Cache-Control": cache_control,
        },
    )
