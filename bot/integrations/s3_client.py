from pathlib import Path
import tempfile
from typing import (
    Any,
    Dict,
    List,
    Optional,
)

import aiobotocore.session
from botocore.exceptions import ClientError

from bot.settings import settings as s


class S3Client:
    def __init__(self) -> None:
        self.__endpoint = s.S3_ENDPOINT_URL
        self.__bucket: str = s.S3_BUCKET  # type: ignore[assignment]
        self.__access_key: str = s.S3_ACCESS_KEY  # type: ignore[assignment]
        self.__secret_key: str = s.S3_SECRET_KEY.get_secret_value()  # type: ignore[union-attr]
        self.__region: str = s.S3_REGION
        self.__session = aiobotocore.session.get_session()

    def _create_client(self) -> Any:
        return self.__session.create_client(
            "s3",
            endpoint_url=self.__endpoint,
            region_name=self.__region,
            aws_access_key_id=self.__access_key,
            aws_secret_access_key=self.__secret_key,
        )

    async def list_objects(
        self,
        prefix: str,
        suffix: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        objects: List[Dict[str, Any]] = []
        continuation_token: Optional[str] = None

        async with self._create_client() as client:
            while True:
                params: Dict[str, Any] = {
                    "Bucket": self.__bucket,
                    "Prefix": prefix,
                    "MaxKeys": 1000,
                }
                if continuation_token:
                    params["ContinuationToken"] = continuation_token

                response = await client.list_objects_v2(**params)
                for obj in response.get("Contents", []):
                    key: str = obj["Key"]
                    if suffix is None or key.endswith(suffix):
                        objects.append(obj)

                if response.get("IsTruncated"):
                    continuation_token = response["NextContinuationToken"]
                else:
                    break

        return objects

    async def list_common_prefixes(self, prefix: str) -> List[str]:
        prefixes: List[str] = []

        async with self._create_client() as client:
            paginator = client.get_paginator("list_objects_v2")
            async for page in paginator.paginate(
                Bucket=self.__bucket,
                Prefix=prefix,
                Delimiter="/",
            ):
                for cp in page.get("CommonPrefixes", []):
                    prefixes.append(cp["Prefix"])

        return prefixes

    async def download(self, key: str) -> bytes:
        async with self._create_client() as client:
            response = await client.get_object(
                Bucket=self.__bucket,
                Key=key,
            )
            async with response["Body"] as stream:
                return await stream.read()

    async def download_to_temp(self, key: str) -> Path:
        data = await self.download(key)
        suffix = Path(key).suffix or ".bin"
        fd, tmp_path = tempfile.mkstemp(suffix=suffix)

        with open(fd, "wb") as f:
            f.write(data)

        return Path(tmp_path)

    async def exists(self, key: str) -> bool:
        async with self._create_client() as client:
            try:
                await client.head_object(
                    Bucket=self.__bucket,
                    Key=key,
                )
                return True
            except ClientError:
                return False

    async def generate_presigned_url(
        self,
        key: str,
        expires_in: int = 3600,
    ) -> str:
        async with self._create_client() as client:
            return await client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.__bucket, "Key": key},
                ExpiresIn=expires_in,
            )
