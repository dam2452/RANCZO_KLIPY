import json
import logging
import os
from typing import Optional

from elasticsearch import (
    AsyncElasticsearch,
    helpers,
)
import urllib3

from bot.settings import Settings
from bot.utils.database import DatabaseManager

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# fixme: zgrupowac to w klase?
# fixme: sensowne exceptiony rzucac
# fixme: nie lapac wszystkiego jak zwierze
# fixme: przeczyscic te funkcje


async def try_connect_to_elasticsearch() -> Optional[AsyncElasticsearch]:
    try:
        es = AsyncElasticsearch(
            hosts=[Settings.ES_HOST],
            basic_auth=(Settings.ES_USER, Settings.ES_PASS),
            verify_certs=False,
        )
        if not await es.ping():
            raise ValueError("Failed to connect to Elasticsearch.")
        logger.info("Connected to Elasticsearch.")
        await DatabaseManager.log_system_message("INFO", "Connected to Elasticsearch.")
        return es
    except Exception as e:
        logger.error(f"Connection to Elasticsearch failed: {e}")
        await DatabaseManager.log_system_message("ERROR", f"Connection to Elasticsearch failed: {e}")
        raise


async def delete_all_indices(es: AsyncElasticsearch) -> None:
    try:
        all_indices = await es.indices.get(index="_all")
        if not all_indices:
            logger.info("No indices to delete.")
            await DatabaseManager.log_system_message("INFO", "No indices to delete.")
            return

        for index in all_indices:
            await es.indices.delete(index=index)
            logger.info(f"Deleted index: {index}")
            await DatabaseManager.log_system_message("INFO", f"Deleted index: {index}")
        logger.info("All indices have been deleted.")
        await DatabaseManager.log_system_message("INFO", "All indices have been deleted.")
    except Exception as e:
        logger.error(f"Error deleting indices: {e}")
        await DatabaseManager.log_system_message("ERROR", f"Error deleting indices: {e}")
        raise


    # fixme: kto to panu tak spierdolil xDD
#fixme: XDDDD Panie o był jednorazowy kod i zadziałał XDD przynajmniej wtedy był jednorazowy bo teraz jak chcemy kiepskich itp to się zmieniło XDDDD
async def index_transcriptions(base_path: str, es: AsyncElasticsearch) -> None:
    actions = []
    for season_dir in os.listdir(base_path):
        season_path = os.path.join(base_path, season_dir)
        if os.path.isdir(season_path):
            for episode_file in os.listdir(season_path):
                if episode_file.endswith('.json'):
                    file_path = os.path.join(season_path, episode_file)
                    logger.info(f"Processing file: {file_path}")
                    await DatabaseManager.log_system_message("INFO", f"Processing file: {file_path}")

                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        episode_info = data.get('episode_info', {})

                        video_path = os.path.join("bot/RANCZO-WIDEO", season_dir, episode_file.replace('.json', '.mp4'))
                        video_path = video_path.replace("\\", "/")

                        for segment in data.get('segments', []):
                            segment['episode_info'] = episode_info
                            segment['video_path'] = video_path

                            actions.append({
                                "_index": "ranczo-transcriptions",
                                "_source": segment,
                            })

    if actions:
        logger.info(f"Indexing {len(actions)} segments.")
        await DatabaseManager.log_system_message("INFO", f"Indexing {len(actions)} segments.")
        await helpers.async_bulk(es, actions)
        logger.info("Data indexed successfully.")
        await DatabaseManager.log_system_message("INFO", "Data indexed successfully.")
    else:
        logger.info("No data to index.")
        await DatabaseManager.log_system_message("INFO", "No data to index.")


async def print_one_transcription(es: AsyncElasticsearch, index: str = "ranczo-transcriptions") -> None:
    try:
        response = await es.search(index=index, size=1)
        if response['hits']['hits']:
            document = response['hits']['hits'][0]['_source']
            document['video_path'] = document['video_path'].replace("\\", "/")
            readable_output = f"Document ID: {response['hits']['hits'][0]['_id']}\n" \
                              f"Episode Info: {document['episode_info']}\n" \
                              f"Video Path: {document['video_path']}\n" \
                              f"Segment Text: {document.get('text', 'No text available')}\n" \
                              f"Timestamp: {document.get('timestamp', 'No timestamp available')}"
            logger.info("Retrieved document:")
            print(readable_output)
            await DatabaseManager.log_system_message("INFO", "Retrieved document:\n" + readable_output)
        else:
            logger.info("No documents found.")
            await DatabaseManager.log_system_message("INFO", "No documents found.")
    except Exception as e:
        logger.error(f"Error retrieving document: {e}")
        await DatabaseManager.log_system_message("ERROR", f"Error retrieving document: {e}")
        raise


async def main() -> None:
    es_client = await try_connect_to_elasticsearch()
    if es_client:
        try:
            await delete_all_indices(es_client)
            await index_transcriptions(base_path="../RANCZO-TRANSKRYPCJE", es=es_client)
            await print_one_transcription(es_client)
        finally:
            await es_client.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
