import pytest

import bot.responses.not_sending_videos.save_clip_handler_responses as save_msg
import bot.responses.sending_videos.compile_selected_clips_handler_responses as comp_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestMergeClipsCommand(BaseTest):

    @pytest.mark.quick
    async def test_merge_multiple_clips(self):
        await self.send_command('/klip geniusz')
        await  self.expect_command_result_contains(
            '/zapisz klip1',
            [save_msg.get_clip_saved_successfully_message("klip1")],
        )
        await  self.send_command('/klip kozioł')
        await self.expect_command_result_contains(
            '/zapisz klip2',
            [save_msg.get_clip_saved_successfully_message("klip2")],
        )
        await self.send_command('/klip uczniowie')
        await self.expect_command_result_contains(
            '/zapisz klip3',
            [save_msg.get_clip_saved_successfully_message("klip3")],
        )

        await self.assert_file_matches(await self.send_command('/polaczklipy 1 2 3'), 'merged_clip_1_2_3.mp4')


    @pytest.mark.quick
    def test_merge_invalid_clip_numbers(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains(
            '/zapisz klip1',
            [save_msg.get_clip_saved_successfully_message("klip1")],
        )
        self.send_command('/klip kozioł')
        self.expect_command_result_contains(
            '/zapisz klip2',
            [save_msg.get_clip_saved_successfully_message("klip2")],
        )

        self.expect_command_result_contains(
            '/polaczklipy 1 5',
            [comp_msg.get_invalid_args_count_message()],
        )



    @pytest.mark.quick
    async def test_merge_single_clip(self):
        await self.send_command('/klip geniusz')
        await self.expect_command_result_contains(
            '/zapisz klip1',
            [save_msg.get_clip_saved_successfully_message("klip1")],
        )

        await self.assert_file_matches(await self.send_command('/polaczklipy 1'), 'merged_single_clip_1.mp4')



    @pytest.mark.long
    def test_merge_no_clips(self):
        self.expect_command_result_contains(
            '/polaczklipy 1 2',
            [comp_msg.get_no_matching_clips_found_message()],
        )

    @pytest.mark.long
    async def test_merge_clips_with_special_characters_in_name(self):
        await self.send_command('/klip geniusz')
        await self.expect_command_result_contains(
            '/zapisz klip@specjalny!',
            [save_msg.get_clip_saved_successfully_message("klip@specjalny!")],
        )

        await self.assert_file_matches(await self.send_command('/polaczklipy 1'), 'merged_special_name_clip.mp4')
