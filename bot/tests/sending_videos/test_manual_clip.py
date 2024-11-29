import pytest

import bot.responses.sending_videos.manual_clip_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestManualClipCommand(BaseTest):

    @pytest.mark.quick
    async def test_cut_clip_valid_range(self):
        await self.assert_command_result_file_matches(
            await self.send_command('/wytnij S07E06 36:47.50 36:49.00'),
            'cut_S07E06_36-47.50_36-49.00.mp4',
        )

    @pytest.mark.quick
    def test_cut_clip_invalid_time_format(self):
        self.expect_command_result_contains(
            '/wytnij S07E06 abc 36:49.00',
            [msg.get_incorrect_time_format_message()],
        )

    @pytest.mark.quick
    def test_cut_clip_nonexistent_episode(self):
        self.expect_command_result_contains(
            '/wytnij S99E99 00:00.00 00:10.00',
            [msg.get_video_file_not_exist_message()],
        )

    @pytest.mark.long
    def test_cut_clip_end_time_before_start_time(self):
        self.expect_command_result_contains(
            '/wytnij S07E06 36:49.00 36:47.50',
            [msg.get_end_time_earlier_than_start_message()],
        )

    @pytest.mark.long
    async def test_cut_clip_large_time_range(self):
        await self.assert_command_result_file_matches(
            await self.send_command('/wytnij S07E06 40:00.00 41:00.00', timeout=30),
            'cut_S07E06_40-00.00_41-00.00.mp4',
        )

    @pytest.mark.long
    def test_cut_clip_exact_episode_length(self):
        self.expect_command_result_contains(
            '/wytnij S07E06 00:00.00 45:00.00',
            [msg.get_limit_exceeded_clip_duration_message()],
        )
