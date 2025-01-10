import argparse
import json
import logging
from pathlib import Path
from typing import List

from elasticsearch import (
    AsyncElasticsearch,
    helpers,
)
import urllib3

from bot.database.database_manager import DatabaseManager
from bot.settings import settings as s
from bot.utils.log import log_system_message

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ElasticSearchManager:
    @staticmethod
    async def connect_to_elasticsearch(logger: logging.Logger) -> AsyncElasticsearch:
        es = AsyncElasticsearch(
            hosts=[s.ES_HOST],
            basic_auth=(s.ES_USER, s.ES_PASS),
            verify_certs=False,
        )
        if not await es.ping():
            raise ConnectionError("Failed to connect to Elasticsearch.")
        await log_system_message(logging.INFO, "Connected to Elasticsearch.", logger)
        return es

    @staticmethod
    async def create_index(es: AsyncElasticsearch, index_name: str, logger: logging.Logger) -> None:
        mapping = {
            "mappings": {
                "properties": {
                    # "episode_info": {"type": "object"},  # Zakomentowane
                    "text": {"type": "text"},
                    "start": {"type": "float"},
                    "end": {"type": "float"},
                    "video_path": {"type": "keyword"},
                }
            }
        }

        try:
            if not await es.indices.exists(index=index_name):
                await es.indices.create(index=index_name, body=mapping)
                await log_system_message(logging.INFO, f"Index '{index_name}' created.", logger)
            else:
                await log_system_message(logging.INFO, f"Index '{index_name}' already exists.", logger)
        except Exception as e:
            await log_system_message(logging.ERROR, f"Error creating index '{index_name}': {str(e)}", logger)

    @staticmethod
    async def delete_all_indices(es: AsyncElasticsearch, logger: logging.Logger) -> None:
        all_indices = await es.indices.get(index="_all")
        if not all_indices:
            await log_system_message(logging.INFO, "No indices to delete.", logger)
            return

        for index in all_indices:
            await es.indices.delete(index=index)
            await log_system_message(logging.INFO, f"Deleted index: {index}", logger)
        await log_system_message(logging.INFO, "All indices have been deleted.", logger)

    @staticmethod
    async def print_one_transcription(
        es: AsyncElasticsearch,
        logger: logging.Logger,
        index_name: str = s.ES_TRANSCRIPTION_INDEX,
    ) -> None:
        response = await es.search(index=index_name, size=1)
        if response["hits"]["hits"]:
            document = response["hits"]["hits"][0]["_source"]

            if "video_path" in document and isinstance(document["video_path"], str):
                document["video_path"] = document["video_path"].replace("\\", "/")

            readable_output = (
                f"Document ID: {response['hits']['hits'][0]['_id']}\n"
                # Zakomentowane:
                # f"Episode Info: {document.get('episode_info', {})}\n"
                f"Video Path: {document.get('video_path', 'No video_path')}\n"
                f"Segment Text: {document.get('text', 'No text available')}\n"
                f"Timestamp: {document.get('timestamp', 'No timestamp available')}"
            )
            await log_system_message(
                logging.INFO, "Retrieved document:\n" + readable_output, logger,
            )
        else:
            await log_system_message(logging.INFO, "No documents found.", logger)

    @staticmethod
    async def index_transcriptions(
        base_path: Path,
        video_base_path: Path,
        es: AsyncElasticsearch,
        logger: logging.Logger,
        index_name: str = s.ES_TRANSCRIPTION_INDEX,
    ) -> None:
        actions = await ElasticSearchManager.__load_all_seasons_actions(
            base_path=base_path,
            video_base_path=video_base_path,
            logger=logger,
            index_name=index_name,
        )

        if actions:
            await log_system_message(
                logging.INFO,
                f"Indexing {len(actions)} segments into '{index_name}'.",
                logger,
            )
            await helpers.async_bulk(es, actions)
            await log_system_message(
                logging.INFO, "Data indexed successfully.", logger,
            )
        else:
            await log_system_message(logging.INFO, "No data to index.", logger)

    @staticmethod
    async def __load_all_seasons_actions(
        base_path: Path,
        video_base_path: Path,
        logger: logging.Logger,
        index_name: str,
    ) -> List[json]:
        actions = []
        for season_path in base_path.iterdir():
            if not season_path.is_dir():
                continue

            season_actions = await ElasticSearchManager.__load_season(
                logger=logger,
                season_path=season_path,
                video_base_path=video_base_path,
                index_name=index_name,
            )
            actions += season_actions
        return actions

    @staticmethod
    async def __load_season(
        logger: logging.Logger,
        season_path: Path,
        video_base_path: Path,
        index_name: str,
    ) -> List[json]:
        season_actions = []
        season_dir = season_path.name

        for episode_file in season_path.iterdir():
            if episode_file.suffix != ".json":
                continue

            await log_system_message(
                logging.INFO, f"Processing file: {episode_file}", logger,
            )
            episode_actions = await ElasticSearchManager.__load_episode(
                episode_file=episode_file,
                season_dir=season_dir,
                video_base_path=video_base_path,
                index_name=index_name,
            )
            season_actions += episode_actions

        return season_actions

    @staticmethod
    async def __load_episode(
            episode_file: Path,
            season_dir: str,
            video_base_path: Path,
            index_name: str,
    ) -> List[json]:
        actions = []
        with episode_file.open("r", encoding="utf-8") as f:
            data = json.load(f)

            # Tymczasowo zakomentowane
            # episode_info = data.get("episode_info", {})
            video_file_name = episode_file.stem + ".mp4"

            video_path = video_base_path / season_dir / video_file_name
            video_path_str = video_path.as_posix()

            for segment in data.get("segments", []):
                # Tymczasowo zakomentowane
                # segment["episode_info"] = episode_info
                segment["video_path"] = video_path_str

                actions.append(
                    {
                        "_index": index_name,
                        "_source": segment,
                    },
                )

        return actions


async def main(logger: logging.Logger) -> None:
    parser = argparse.ArgumentParser(description="Elasticsearch transcription indexing tool.")
    parser.add_argument(
        "--base-path",
        required=True,
        type=str,
        help="Path to the directory containing transcription JSON files (e.g., '../RANCZO-TRANSKRYPCJE').",
    )
    parser.add_argument(
        "--video-base-path",
        required=True,
        type=str,
        help="Path to the directory containing video files (e.g., '../RANCZO-WIDEO').",
    )
    parser.add_argument(
        "--index-name",
        required=True,
        type=str,
        help="Name of the Elasticsearch index (e.g., 'ranczo-transcriptions').",
    )
    parser.add_argument(
        "--delete-existing",
        action="store_true",
        help="Delete existing Elasticsearch indices before indexing.",
    )

    args = parser.parse_args()

    base_path = Path(args.base_path)
    video_base_path = Path(args.video_base_path)
    index_name = args.index_name

    await DatabaseManager.init_pool()

    es_client = await ElasticSearchManager.connect_to_elasticsearch(logger)
    try:
        if args.delete_existing:
            await ElasticSearchManager.delete_all_indices(es_client, logger)

        await ElasticSearchManager.create_index(es_client, index_name, logger)

        await ElasticSearchManager.index_transcriptions(
            base_path=base_path,
            video_base_path=video_base_path,
            es=es_client,
            logger=logger,
            index_name=index_name,
        )

        await ElasticSearchManager.print_one_transcription(
            es=es_client,
            logger=logger,
            index_name=index_name,
        )
    finally:
        await es_client.close()


if __name__ == "__main__":
    import asyncio
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(logging.getLogger(__name__)))
