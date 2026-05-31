import io
import logging
from pathlib import Path
import re
from typing import (
    Any,
    Dict,
    List,
    Optional,
)
import zipfile

from bot.integrations.s3_client import S3Client
from bot.services.reindex.zip_extractor import ZipExtractor


class S3StorageStrategy:
    def __init__(self, logger: logging.Logger, s3_client: S3Client) -> None:
        self.__logger = logger
        self.__s3_client = s3_client

    async def scan_all_series(self) -> List[str]:
        top_prefixes = await self.__s3_client.list_common_prefixes("")
        series_set: set[str] = set()

        for prefix in top_prefixes:
            series_name = prefix.rstrip("/")
            sub_prefixes = await self.__s3_client.list_common_prefixes(prefix)
            has_seasons = any(
                re.match(r'^.*S\d{2}/$', sp) for sp in sub_prefixes
            )
            if has_seasons:
                series_set.add(series_name)

        return sorted(series_set)

    async def scan_series_zips(self, series_name: str) -> List[str]:
        objects = await self.__s3_client.list_objects(
            prefix=f"{series_name}/",
            suffix=".zip",
        )
        keys = [obj["Key"] for obj in objects]
        return sorted(keys)

    async def scan_series_mp4s(self, series_name: str) -> Dict[str, str]:
        objects = await self.__s3_client.list_objects(
            prefix=f"{series_name}/",
            suffix=".mp4",
        )
        mp4_map: Dict[str, str] = {}
        for obj in objects:
            key: str = obj["Key"]
            episode_code = self.__extract_episode_code(key)
            if episode_code:
                mp4_map[episode_code] = key

        return mp4_map

    async def read_zip_to_memory(self, zip_key: str) -> Dict[str, io.BytesIO]:
        data = await self.__s3_client.download(zip_key)
        extracted_files: Dict[str, io.BytesIO] = {}

        try:
            with zipfile.ZipFile(io.BytesIO(data), "r") as zf:
                for file_info in zf.infolist():
                    if not file_info.filename.endswith(".jsonl"):
                        continue

                    content = zf.read(file_info.filename)
                    buffer = io.BytesIO(content)

                    jsonl_type = ZipExtractor.detect_type_from_filename(
                        file_info.filename,
                    )
                    if jsonl_type:
                        extracted_files[jsonl_type] = buffer

        except zipfile.BadZipFile as exc:
            raise ValueError(f"Invalid zip from S3: {zip_key}") from exc

        return extracted_files

    def resolve_video_path(
        self,
        doc: Dict[str, Any],
        mp4_key: Optional[str],
    ) -> Dict[str, Any]:
        if "video_path" not in doc:
            return doc

        if mp4_key is None:
            self.__logger.warning(
                "No MP4 key provided for document, keeping old: %s",
                doc.get("video_path"),
            )
            return doc

        doc["video_path"] = mp4_key
        return doc

    async def resolve_to_local_file(self, video_key: str) -> Path:
        return await self.__s3_client.download_to_temp(video_key)

    @staticmethod
    def __extract_episode_code(key: str) -> Optional[str]:
        match = re.search(r"(S\d{2}E\d{2})", key, re.IGNORECASE)
        if match:
            return match.group(1).upper()
        return None
