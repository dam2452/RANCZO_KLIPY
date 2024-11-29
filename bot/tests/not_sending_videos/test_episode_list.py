import pytest

import bot.responses.not_sending_videos.episode_list_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestEpisodesListsCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_episodes_for_valid_season(self):
        response = await self.send_command('/odcinki 4')
        await self.assert_message_hash_matches(response, expected_key="episode_list_season_4.message")

    @pytest.mark.asyncio
    async def test_episodes_for_nonexistent_season(self):
        response = await self.send_command('/odcinki 99')
        self.assert_response_contains(response, [msg.get_no_episodes_found_message(99)])

    @pytest.mark.asyncio
    async def test_episodes_invalid_arguments(self):
        response = await self.send_command('/odcinki')
        self.assert_response_contains(response, [msg.get_invalid_args_count_message()])

    @pytest.mark.asyncio
    async def test_episodes_long_list(self):
        response = await self.send_command('/odcinki 3')
        await self.assert_message_hash_matches(response, expected_key="episode_list_season_3_long.message")

    @pytest.mark.asyncio
    async def test_episodes_for_season_11(self):
        response = await self.send_command('/odcinki 11')
        self.assert_response_contains(response, [msg.get_season_11_petition_message()])
