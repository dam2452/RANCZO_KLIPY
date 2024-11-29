import pytest

import bot.responses.sending_videos.manual_clip_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestManualClipCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_cut_clip_valid_range(self):
        response = await self.send_command('/wytnij S07E06 36:47.50 36:49.00')
        await self.assert_command_result_file_matches(
            response,
            'cut_S07E06_36-47.50_36-49.00.mp4',
        )

    @pytest.mark.asyncio
    async def test_cut_clip_invalid_time_format(self):
        response = await self.send_command('/wytnij S07E06 abc 36:49.00')
        self.assert_response_contains(
            response,
            [msg.get_incorrect_time_format_message()],
        )

    @pytest.mark.asyncio
    async def test_cut_clip_nonexistent_episode(self):
        response = await self.send_command('/wytnij S99E99 00:00.00 00:10.00')
        self.assert_response_contains(
            response,
            [msg.get_video_file_not_exist_message()],
        )

    # @pytest.mark.asyncio
    # async def test_cut_clip_end_time_before_start_time(self):
    #     response = await self.send_command('/wytnij S07E06 36:49.00 36:47.50')
    #     self.assert_response_contains(
    #         response,
    #         [msg.get_end_time_earlier_than_start_message()]
    #     )

    @pytest.mark.asyncio
    async def test_cut_clip_large_time_range(self):
        response = await self.send_command('/wytnij S07E06 40:00.00 41:00.00', timeout=30)
        await self.assert_command_result_file_matches(
            response,
            'cut_S07E06_40-00.00_41-00.00.mp4',
        )

    # @pytest.mark.asyncio
    # async def test_cut_clip_exact_episode_length(self):
    #     response = await self.send_command('/wytnij S07E06 00:00.00 45:00.00', timeout=30)
    #     self.assert_response_contains(
    #         response,
    #         [msg.get_limit_exceeded_clip_duration_message()]
    #     )
