import json
import logging
import os

from elasticsearch import (
    AsyncElasticsearch,
    helpers,
)
import urllib3

from bot.settings import Settings
from bot.utils.log import log_system_message

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# fixme: zgrupowac to w klase?
# fixme: przeczyscic te funkcje


async def connect_to_elasticsearch() -> AsyncElasticsearch:
    es = AsyncElasticsearch(
        hosts=[Settings.ES_HOST],
        basic_auth=(Settings.ES_USER, Settings.ES_PASS),
        verify_certs=False,
    )
    if not await es.ping():
        raise ConnectionError("Failed to connect to Elasticsearch.")
    await log_system_message(logging.INFO, "Connected to Elasticsearch.", logger)
    return es


async def delete_all_indices(es: AsyncElasticsearch) -> None:
    all_indices = await es.indices.get(index="_all")
    if not all_indices:
        await log_system_message(logging.INFO, "No indices to delete.", logger)
        return

    for index in all_indices:
        await es.indices.delete(index=index)
        await log_system_message(logging.INFO, f"Deleted index: {index}", logger)
    await log_system_message(logging.INFO, "All indices have been deleted.", logger)


async def index_transcriptions(base_path: str, es: AsyncElasticsearch) -> None:
    actions = []
    for season_dir in os.listdir(base_path):
        season_path = os.path.join(base_path, season_dir)
        if os.path.isdir(season_path):
            for episode_file in os.listdir(season_path):
                if episode_file.endswith('.json'):
                    file_path = os.path.join(season_path, episode_file)
                    await log_system_message(logging.INFO, f"Processing file: {file_path}", logger)

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
        await log_system_message(logging.INFO, f"Indexing {len(actions)} segments.", logger)
        await helpers.async_bulk(es, actions)
        await log_system_message(logging.INFO, "Data indexed successfully.", logger)
    else:
        await log_system_message(logging.INFO, "No data to index.", logger)


async def print_one_transcription(es: AsyncElasticsearch, index: str = "ranczo-transcriptions") -> None:
    response = await es.search(index=index, size=1)
    if response['hits']['hits']:
        document = response['hits']['hits'][0]['_source']
        document['video_path'] = document['video_path'].replace("\\", "/")
        readable_output = f"Document ID: {response['hits']['hits'][0]['_id']}\n" \
                          f"Episode Info: {document['episode_info']}\n" \
                          f"Video Path: {document['video_path']}\n" \
                          f"Segment Text: {document.get('text', 'No text available')}\n" \
                          f"Timestamp: {document.get('timestamp', 'No timestamp available')}"
        await log_system_message(logging.INFO, "Retrieved document:\n" + readable_output, logger)
    else:
        await log_system_message(logging.INFO, "No documents found.", logger)


async def main() -> None:
    es_client = await connect_to_elasticsearch()
    try:
        await delete_all_indices(es_client)
        await index_transcriptions(base_path="../RANCZO-TRANSKRYPCJE", es=es_client)
        await print_one_transcription(es_client)
    finally:
        await es_client.close()


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())