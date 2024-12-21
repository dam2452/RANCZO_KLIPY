import asyncio
import logging

import pytest
from telethon.sync import TelegramClient

from bot.database.database_manager import DatabaseManager
import bot.tests.messages as msg
from bot.tests.settings import settings as s

logger = logging.getLogger(__name__)

@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_pool():
    await DatabaseManager.init_pool(
        host=s.TEST_POSTGRES_HOST,
        port=s.TEST_POSTGRES_PORT,
        database=s.TEST_POSTGRES_DB,
        user=s.TEST_POSTGRES_USER,
        password=s.TEST_POSTGRES_PASSWORD,
    )
    await DatabaseManager.init_db()
    yield
    await DatabaseManager.pool.close()

@pytest.fixture(scope="class")
def telegram_client():
    client = TelegramClient(
        s.SESSION,
        s.API_ID,
        s.API_HASH,
    )
    client.start(password=s.PASSWORD, phone=s.PHONE)

    logger.info(msg.client_started())
    yield client
    client.disconnect()
    logger.info(msg.client_disconnected())

@pytest.fixture(autouse=True)
async def prepare_database():
    await DatabaseManager.clear_test_db()
    logger.info("The test database has been cleared.")

    await DatabaseManager.set_default_admin(
        user_id=s.DEFAULT_ADMIN,
        username=s.ADMIN_USERNAME,
        full_name=s.ADMIN_FULL_NAME,
    )
    logger.info(f"Default admin with user_id {s.DEFAULT_ADMIN} has been set.")
