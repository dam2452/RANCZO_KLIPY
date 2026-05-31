import io
import logging
from pathlib import Path
from typing import (
    Dict,
    List,
    Optional,
)

from bot.services.reindex.series_scanner import SeriesScanner
from bot.services.reindex.video_path_transformer import VideoPathTransformer
from bot.services.reindex.zip_extractor import ZipExtractor
from bot.settings import settings as s


class LocalStorageStrategy:
    def __init__(self, logger: logging.Logger) -> None:
        self.__logger = logger
        self.__scanner = SeriesScanner(logger)
        self.__zip_extractor = ZipExtractor(logger)
        self.__video_transformer = VideoPathTransformer(logger)

    async def scan_all_series(self) -> List[str]:
        return self.__scanner.scan_all_series()

    async def scan_series_zips(self, series_name: str) -> List[str]:
        paths = self.__scanner.scan_series_zips(series_name)
        return [str(p) for p in paths]

    async def scan_series_mp4s(self, series_name: str) -> Dict[str, str]:
        mp4_map = self.__scanner.scan_series_mp4s(series_name)
        return {code: str(path) for code, path in mp4_map.items()}

    async def read_zip_to_memory(self, zip_key: str) -> Dict[str, io.BytesIO]:
        return self.__zip_extractor.extract_to_memory(Path(zip_key))

    def resolve_video_path(
        self,
        doc: Dict[str, object],
        mp4_key: Optional[str],
    ) -> Dict[str, object]:
        mp4_path = Path(mp4_key) if mp4_key else None
        return self.__video_transformer.transform_video_path(doc, mp4_path)

    async def resolve_to_local_file(self, video_key: str) -> Path:
        resolved = Path(s.VIDEO_DATA_DIR) / video_key
        if not resolved.exists():
            self.__logger.error(f"Video file does not exist: {resolved}")
        if not str(resolved.resolve()).startswith(str(Path(s.VIDEO_DATA_DIR).resolve())):
            raise ValueError(f"Access denied: path outside VIDEO_DATA_DIR: {resolved}")
        return resolved
