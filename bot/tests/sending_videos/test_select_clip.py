import pytest

import bot.responses.sending_videos.select_clip_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSelectClipCommand(BaseTest):

    @pytest.mark.quick
    async def test_select_existing_clip(self):
        await self.expect_command_result_contains('/szukaj kozioł', ["Wyniki wyszukiwania"])
        await self.assert_file_matches(await self.send_command('/wybierz 1'), 'kozioł_clip_1.mp4')

    @pytest.mark.quick
    def test_select_nonexistent_clip(self):
        self.expect_command_result_contains('/szukaj Anglii', ["Wyniki wyszukiwania"])
        self.expect_command_result_contains('/wybierz 100', [msg.get_invalid_segment_number_message()])

    @pytest.mark.long
    async def test_select_multiple_clips_in_sequence(self):
        await self.expect_command_result_contains('/szukaj kozioł', ["Wyniki wyszukiwania"])
        await self.assert_file_matches(await self.send_command('/wybierz 1'), 'kozioł_clip_select_1.mp4')
        await self.assert_file_matches(await self.send_command('/wybierz 2'), 'kozioł_clip_select_2.mp4')
