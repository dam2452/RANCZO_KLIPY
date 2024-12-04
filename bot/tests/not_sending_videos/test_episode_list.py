import pytest

import bot.responses.not_sending_videos.episode_list_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestEpisodesListsCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_episodes_for_valid_season(self):
        season_number = 4
        response = await self.send_command(f'/odcinki {season_number}')
        await self.assert_message_hash_matches(response, expected_key=f"episode_list_season_{season_number}.message")

    @pytest.mark.asyncio
    async def test_episodes_for_nonexistent_season(self):
        season_number = 99
        response = await self.send_command(f'/odcinki {season_number}')
        self.assert_response_contains(response, [msg.get_no_episodes_found_message(season_number)])

    @pytest.mark.asyncio
    async def test_episodes_invalid_arguments(self):
        response = await self.send_command('/odcinki')
        self.assert_response_contains(response, [msg.get_invalid_args_count_message()])

    @pytest.mark.asyncio
    async def test_episodes_long_list(self):
        season_number = 3
        response = await self.send_command(f'/odcinki {season_number}')
        await self.assert_message_hash_matches(response, expected_key=f"episode_list_season_{season_number}_long.message")

    @pytest.mark.asyncio
    async def test_episodes_for_season_11(self):
        season_number = 11
        response = await self.send_command(f'/odcinki {season_number}')
        self.assert_response_contains(response, [msg.get_season_11_petition_message()])
