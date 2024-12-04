import pytest

import bot.responses.sending_videos.select_clip_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSelectClipCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_select_valid_segment(self):
        await self.expect_command_result_contains(
            '/szukaj geniusz', ["search_geniusz_results.message"],
        )

        # Wybór segmentu
        await self.expect_command_result_contains(
            '/wybierz 1', ['selected_geniusz_clip_1.mp4'],
        )

    @pytest.mark.asyncio
    async def test_select_no_previous_search(self):
        await self.expect_command_result_contains(
            '/wybierz 1', [msg.get_no_previous_search_message()],
        )
    @pytest.mark.asyncio
    async def test_select_invalid_segment_number(self):
        await self.expect_command_result_contains(
            '/szukaj geniusz', ["search_geniusz_results.message"],
        )

        await self.expect_command_result_contains(
            '/wybierz 999', [msg.get_invalid_segment_number_message()],
        )

    # @pytest.mark.asyncio
    # async def test_select_clip_duration_exceeds_limit(self):
    #     await self.expect_command_result_contains(
    #         '/szukaj długi_segment', ["search_long_segment_results.message"]
    #     )
    #
    #     await self.expect_command_result_contains(
    #         '/wybierz 2', [msg.get_limit_exceeded_clip_duration_message()]
    #     )
