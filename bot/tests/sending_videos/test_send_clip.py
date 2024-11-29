import pytest

import bot.responses.not_sending_videos.save_clip_handler_responses as save_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSendClipCommand(BaseTest):

    @pytest.mark.quick
    async def test_send_existing_clip(self):
        clip_name = "klip1"
        await self.send_command('/klip geniusz')
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [save_msg.get_clip_saved_successfully_message(clip_name)],
        )
        await self.assert_command_result_file_matches(
            await self.send_command(f'/wyslij {clip_name}'),
            'geniusz_klip1_from_send.mp4',
        )

    @pytest.mark.quick
    async def test_send_nonexistent_clip(self):
        clip_name = "klip1337"
        await self.expect_command_result_contains(
            f'/wyslij {clip_name}',
            [save_msg.get_clip_name_not_provided_message()],
        )

    @pytest.mark.quick
    async def test_send_clip_with_no_saved_clips(self):
        clip_name = "klip1"
        await self.expect_command_result_contains(
            f'/wyslij {clip_name}',
            [save_msg.get_clip_name_not_provided_message()],
        )

    @pytest.mark.long
    async def test_send_multiple_clips_in_sequence(self):
        clip1_name = "klip1"
        clip2_name = "klip2"
        await self.send_command('/klip geniusz')
        await self.expect_command_result_contains(
            f'/zapisz {clip1_name}',
            [save_msg.get_clip_saved_successfully_message(clip1_name)],
        )
        await self.send_command('/klip kozioł')
        await self.expect_command_result_contains(
            f'/zapisz {clip2_name}',
            [save_msg.get_clip_saved_successfully_message(clip2_name)],
        )

        await self.assert_command_result_file_matches(
            await self.send_command(f'/wyslij {clip1_name}'),
            'geniusz_klip1_from_send.mp4',
        )
        await self.assert_command_result_file_matches(
            await self.send_command(f'/wyslij {clip2_name}'),
            'kozioł_klip2_from_send.mp4',
        )

    @pytest.mark.long
    async def test_send_clip_with_special_characters_in_name(self):
        special_clip_name = "klip@specjalny!"
        await self.send_command('/klip geniusz')
        await self.expect_command_result_contains(
            f'/zapisz {special_clip_name}',
            [save_msg.get_clip_saved_successfully_message(special_clip_name)],
        )
        await self.assert_command_result_file_matches(
            await self.send_command(f'/wyslij {special_clip_name}'),
            'geniusz_clip_special_name_sent.mp4',
        )
