import pytest

from bot.responses.sending_videos.select_clip_handler_responses import (
    get_invalid_segment_number_message,
    get_no_previous_search_message,
)
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSelectClipCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_select_valid_segment(self):
        await self.expect_command_result_hash(
            '/szukaj geniusz',
            expected_key="search_geniusz_results.message",
        )

        select_response = await self.send_command('/wybierz 1')
        await self.assert_command_result_file_matches(select_response, 'selected_geniusz_clip_1.mp4')

    @pytest.mark.asyncio
    async def test_select_no_previous_search(self):
        response = await self.send_command('/wybierz 1')
        self.assert_response_contains(response, [get_no_previous_search_message()])

    @pytest.mark.asyncio
    async def test_select_invalid_segment_number(self):
        await self.expect_command_result_hash(
            '/szukaj geniusz',
            expected_key="search_geniusz_results.message",
        )

        response = await self.send_command('/wybierz 999')
        self.assert_response_contains(response, [get_invalid_segment_number_message()])

    # @pytest.mark.asyncio
    # async def test_select_clip_duration_exceeds_limit(self):
    #     search_response = await self.send_command('/szukaj długi_segment')
    #     await self.assert_message_hash_matches(search_response, expected_key="search_long_segment_results.message")
    #
    #     response = await self.send_command('/wybierz 2')
    #     self.assert_response_contains(response, [msg.get_limit_exceeded_clip_duration_message()])
