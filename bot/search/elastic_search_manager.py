import json
import logging
from pathlib import Path
from typing import List

from elasticsearch import (
    AsyncElasticsearch,
    helpers,
)
import urllib3

from bot.settings import settings
from bot.utils.log import log_system_message

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


class ElasticSearchManager:
    @staticmethod
    async def connect_to_elasticsearch(logger: logging.Logger) -> AsyncElasticsearch:
        es = AsyncElasticsearch(
            hosts=[settings.ES_HOST],
            basic_auth=(settings.ES_USER, settings.ES_PASS),
            verify_certs=False,
        )
        if not await es.ping():
            raise ConnectionError("Failed to connect to Elasticsearch.")
        await log_system_message(logging.INFO, "Connected to Elasticsearch.", logger)
        return es

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
        index: str = settings.ES_TRANSCRIPTION_INDEX,
    ) -> None:
        response = await es.search(index=index, size=1)
        if response["hits"]["hits"]:
            document = response["hits"]["hits"][0]["_source"]
            document["video_path"] = document["video_path"].replace("\\", "/")
            readable_output = (
                f"Document ID: {response['hits']['hits'][0]['_id']}\n"
                f"Episode Info: {document['episode_info']}\n"
                f"Video Path: {document['video_path']}\n"
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
        base_path: Path, es: AsyncElasticsearch, logger: logging.Logger,
    ) -> None:
        actions = await ElasticSearchManager.__load_all_seasons_actions(base_path, logger)

        if actions:
            await log_system_message(
                logging.INFO, f"Indexing {len(actions)} segments.", logger,
            )
            await helpers.async_bulk(es, actions)
            await log_system_message(logging.INFO, "Data indexed successfully.", logger)
        else:
            await log_system_message(logging.INFO, "No data to index.", logger)

    @staticmethod
    async def __load_all_seasons_actions(
        base_path: Path, logger: logging.Logger,
    ) -> List[json]:
        actions = []
        for season_path in base_path.iterdir():
            if not season_path.is_dir():
                continue

            actions += await ElasticSearchManager.__load_season(logger, season_path)
        return actions

    @staticmethod
    async def __load_season(
        logger: logging.Logger, season_path: Path,
    ) -> List[json]:
        season_actions = []
        season_dir = season_path.name

        for episode_file in season_path.iterdir():
            if episode_file.suffix != ".json":
                continue

            await log_system_message(
                logging.INFO, f"Processing file: {episode_file}", logger,
            )
            season_actions += await ElasticSearchManager.__load_episode(
                episode_file, season_dir,
            )

        return season_actions

    @staticmethod
    async def __load_episode(
        episode_file: Path, season_dir: str,
    ) -> List[json]:
        actions = []
        with episode_file.open("r", encoding="utf-8") as f:
            data = json.load(f)
            episode_info = data.get("episode_info", {})

            video_file_name = episode_file.stem + ".mp4"
            video_path = Path("bot/RANCZO-WIDEO") / season_dir / video_file_name
            video_path_str = video_path.as_posix()

            for segment in data.get("segments", []):
                segment["episode_info"] = episode_info
                segment["video_path"] = video_path_str

                actions.append(
                    {
                        "_index": settings.ES_TRANSCRIPTION_INDEX,
                        "_source": segment,
                    },
                )

        return actions


async def main(logger: logging.Logger) -> None:
    es_client = await ElasticSearchManager.connect_to_elasticsearch(logger)
    try:
        await ElasticSearchManager.delete_all_indices(es_client, logger)
        base_path = Path("../RANCZO-TRANSKRYPCJE")
        await ElasticSearchManager.index_transcriptions(
            base_path=base_path, es=es_client, logger=logger,
        )
        await ElasticSearchManager.print_one_transcription(es_client, logger)
    finally:
        await es_client.close()



if __name__ == "__main__":
    import asyncio

    logging.basicConfig(level=logging.INFO)
    asyncio.run(main(logging.getLogger(__name__)))
