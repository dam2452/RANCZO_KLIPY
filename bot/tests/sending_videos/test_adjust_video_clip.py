import pytest

import bot.responses.sending_videos.adjust_video_clip_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestAdjustClipCommand(BaseTest):

    @pytest.mark.quick
    async def test_adjust_clip_with_two_params(self):
        video_name = "geniusz"
        adjust_params = "-5.5 1.5"
        adjusted_filename = f"{video_name} adjusted {adjust_params}.mp4"
        await self.assert_command_result_file_matches(await self.send_command(f"/klip {video_name}"), f"{video_name}.mp4")
        await self.assert_command_result_file_matches(await self.send_command(f"/dostosuj {adjust_params}"), adjusted_filename)

    @pytest.mark.quick
    async def test_adjust_clip_with_three_params(self):
        search_term = "kozioł"
        clip_number = 1
        adjust_params = "10.0 -3"
        adjusted_filename = f"{search_term} clip {clip_number} adjusted {adjust_params}.mp4"
        await self.expect_command_result_contains(f"/szukaj {search_term}", ["Wyniki wyszukiwania"])
        await self.assert_command_result_file_matches(await self.send_command(f"/wybierz {clip_number}"), f"{search_term} clip {clip_number}.mp4")
        await self.assert_command_result_file_matches(await self.send_command(f"/dostosuj {adjust_params}"), adjusted_filename)

    @pytest.mark.long
    async def test_adjust_clip_with_invalid_time_format(self):
        video_name = "geniusz"
        invalid_adjust_params = "-abc 1.2"
        await self.assert_command_result_file_matches(await self.send_command(f"/klip {video_name}"), f"{video_name}.mp4")
        await self.expect_command_result_contains(
            f"/dostosuj {invalid_adjust_params}",
            [msg.get_invalid_args_count_message()],
        )

    @pytest.mark.long
    def test_adjust_nonexistent_clip_number(self):
        search_term = "kozioł"
        invalid_clip_number = 99999
        adjust_params = "10.0 -3"
        self.expect_command_result_contains(f"/szukaj {search_term}", ["Wyniki wyszukiwania"])
        self.expect_command_result_contains(
            f"/dostosuj {invalid_clip_number} {adjust_params}",
            [msg.get_invalid_segment_index_message()],
        )

    @pytest.mark.long
    async def test_adjust_clip_with_large_extension_values(self):
        video_name = "geniusz"
        large_adjust_params = "50 50"
        adjusted_filename = f"{video_name} adjusted {large_adjust_params}.mp4"
        await self.assert_command_result_file_matches(await self.send_command(f"/klip {video_name}"), f"{video_name}.mp4")
        await self.assert_command_result_file_matches(await self.send_command(f"/dostosuj {large_adjust_params}"), adjusted_filename)
