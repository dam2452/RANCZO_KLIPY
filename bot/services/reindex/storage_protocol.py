import io
from pathlib import Path
from typing import (
    Dict,
    List,
    Optional,
    Protocol,
    runtime_checkable,
)


@runtime_checkable
class StorageStrategy(Protocol):
    async def scan_all_series(self) -> List[str]: ...

    async def scan_series_zips(self, series_name: str) -> List[str]: ...

    async def scan_series_mp4s(self, series_name: str) -> Dict[str, str]: ...

    async def read_zip_to_memory(self, zip_key: str) -> Dict[str, io.BytesIO]: ...

    def resolve_video_path(
        self,
        doc: Dict[str, object],
        mp4_key: Optional[str],
    ) -> Dict[str, object]: ...

    async def resolve_to_local_file(self, video_key: str) -> Path: ...
