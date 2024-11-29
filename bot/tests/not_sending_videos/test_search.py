import pytest

import bot.responses.not_sending_videos.search_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSearchCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_search_existing_quote(self):
        response = await self.send_command('/szukaj geniusz')
        await self.assert_message_hash_matches(response, expected_key="search_geniusz_results.message")

    @pytest.mark.asyncio
    async def test_search_nonexistent_quote(self):
        response = await self.send_command('/szukaj brak_cytatu')
        await self.assert_message_hash_matches(response, expected_key="search_brak_cytatu_results.message")

    @pytest.mark.asyncio
    async def test_search_invalid_arguments(self):
        response = await self.send_command('/szukaj')
        self.assert_response_contains(response, [msg.get_invalid_args_count_message()])

    @pytest.mark.asyncio
    async def test_search_long_quote_exceeds_limit(self):
        long_quote = " ".join(["słowo"] * 100)
        response = await self.send_command(f'/szukaj {long_quote}')
        await self.assert_message_hash_matches(response, expected_key="search_long_quote_exceeds_limit.message")

    @pytest.mark.asyncio
    async def test_search_short_alias(self):
        response = await self.send_command('/sz geniusz')
        await self.assert_message_hash_matches(response, expected_key="search_short_alias_geniusz.message")
