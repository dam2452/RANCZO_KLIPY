import pytest

import bot.responses.not_sending_videos.search_list_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestListCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_list_after_successful_search(self):
        search_response = await self.send_command('/szukaj krowa')
        await self.assert_message_hash_matches(search_response, expected_key="search_krowa_results.message")

        list_response = await self.send_command('/lista')
        await self.assert_command_result_file_matches(list_response, 'list_krowa.txt')

    @pytest.mark.asyncio
    async def test_list_no_previous_search(self):
        response = await self.send_command('/lista')
        self.assert_response_contains(response, [msg.get_no_previous_search_results_message()])

    @pytest.mark.asyncio
    async def test_list_with_special_characters_in_search(self):
        search_response = await self.send_command('/szukaj "koń z chmurą"')
        await self.assert_message_hash_matches(search_response, expected_key="search_kon_z_chmura_results.message")

        list_response = await self.send_command('/lista')
        await self.assert_command_result_file_matches(list_response, 'list_kon_z_chmura.txt')
