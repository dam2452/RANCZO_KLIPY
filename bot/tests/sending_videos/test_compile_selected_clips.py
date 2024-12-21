import pytest

import bot.responses.not_sending_videos.save_clip_handler_responses as save_msg
import bot.responses.sending_videos.compile_selected_clips_handler_responses as comp_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestMergeClipsCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_merge_multiple_clips(self):
        clips = [
            {"name": "klip1", "command": "/klip geniusz", "file": "clip_geniusz_saved.mp4"},
            {"name": "klip2", "command": "/klip kozioł", "file": "clip_kozioł_saved.mp4"},
            {"name": "klip3", "command": "/klip uczniowie", "file": "clip_uczniowie_saved.mp4"},
        ]

        for clip in clips:
            response = await self.send_command(clip["command"])
            await self.assert_command_result_file_matches(response, clip["file"])
            await self.expect_command_result_contains(
                f'/zapisz {clip["name"]}',
                [save_msg.get_clip_saved_successfully_message(clip["name"])],
            )

        compile_params = "1 2 3"
        response = await self.send_command(f'/polaczklipy {compile_params}', timeout=60)
        await self.assert_command_result_file_matches(response, f'merged_clip_{compile_params}.mp4')

    @pytest.mark.asyncio
    async def test_merge_invalid_clip_numbers(self):
        response = await self.send_command('/klip geniusz')
        await self.assert_command_result_file_matches(response, 'clip_geniusz_saved.mp4')
        await self.expect_command_result_contains(
            '/zapisz klip1',
            [save_msg.get_clip_saved_successfully_message("klip1")],
        )

        response = await self.send_command('/klip kozioł')
        await self.assert_command_result_file_matches(response, 'clip_kozioł_saved.mp4')
        await self.expect_command_result_contains(
            '/zapisz klip2',
            [save_msg.get_clip_saved_successfully_message("klip2")],
        )

        response = await self.send_command('/polaczklipy 1 5')
        self.assert_response_contains(response, [comp_msg.get_invalid_args_count_message()])

    @pytest.mark.asyncio
    async def test_merge_single_clip(self):
        response = await self.send_command('/klip geniusz')
        await self.assert_command_result_file_matches(response, 'clip_geniusz_saved.mp4')
        await self.expect_command_result_contains(
            '/zapisz klip1',
            [save_msg.get_clip_saved_successfully_message("klip1")],
        )

        response = await self.send_command('/polaczklipy 1')
        await self.assert_command_result_file_matches(response, 'merged_single_clip_1.mp4')

    # @pytest.mark.asyncio
    # async def test_merge_no_clips(self):
    #     response = await self.send_command('/polaczklipy 1 2')
    #     self.assert_response_contains(response, [comp_msg.get_no_matching_clips_found_message()])

    @pytest.mark.asyncio
    async def test_merge_clips_with_special_characters_in_name(self):
        response = await self.send_command('/klip geniusz')
        await self.assert_command_result_file_matches(response, 'clip_geniusz_saved.mp4')
        await self.expect_command_result_contains(
            '/zapisz klip@specjalny!',
            [save_msg.get_clip_saved_successfully_message("klip@specjalny!")],
        )

        response = await self.send_command('/polaczklipy 1')
        await self.assert_command_result_file_matches(response, 'merged_special_name_clip.mp4')
