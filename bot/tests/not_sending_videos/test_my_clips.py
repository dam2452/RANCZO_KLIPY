import pytest

import bot.responses.not_sending_videos.my_clips_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestMyClipsCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_myclips_no_clips(self):
        response = await self.send_command('/mojeklipy')
        self.assert_response_contains(response, [msg.get_no_saved_clips_message()])

    # @pytest.mark.asyncio
    # async def test_myclips_with_regular_clips(self):
    #     await self.send_command('/klip geniusz')
    #     await self.expect_command_result_contains(
    #         '/zapisz pierwszy_klip',
    #         [save_msg.get_clip_saved_successfully_message("pierwszy_klip")],
    #     )
    #
    #     clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
    #     response = msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME)
    #     await self.expect_command_result_contains('/mojeklipy', [response])

    # @pytest.mark.asyncio
    # async def test_myclips_with_compilation(self):
    #     await self.send_command('/klip kompilacja')
    #     await self.expect_command_result_contains(
    #         '/zapisz klip_kompilacja',
    #         [save_msg.get_clip_saved_successfully_message("klip_kompilacja")],
    #     )
    #
    #     clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
    #     for clip in clips:
    #         clip.is_compilation = True
    #     response = msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME)
    #     await self.expect_command_result_contains('/mojeklipy', [response])

    # @pytest.mark.asyncio
    # async def test_myclips_with_long_names(self):
    #     long_name = "klip_" + "g" * 4000
    #     await self.send_command('/klip geniusz')
    #     await self.expect_command_result_contains(
    #         f'/zapisz {long_name}',
    #         [save_msg.get_clip_saved_successfully_message(long_name)],
    #     )
    #
    #     clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
    #     response = msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME)
    #     await self.expect_command_result_contains('/mojeklipy', [response])

    # @pytest.mark.asyncio
    # async def test_myclips_with_special_characters(self):
    #     special_name = "klip_!@#$%^&*()"
    #     await self.send_command('/klip geniusz')
    #     await self.expect_command_result_contains(
    #         f'/zapisz {special_name}',
    #         [save_msg.get_clip_saved_successfully_message(special_name)],
    #     )
    #
    #     clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
    #     response = msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME)
    #     await self.expect_command_result_contains('/mojeklipy', [response])

    # @pytest.mark.asyncio
    # async def test_myclips_empty_durations(self):
    #     await self.send_command('/klip geniusz')
    #     await self.expect_command_result_contains(
    #         '/zapisz klip_bez_czasu',
    #         [save_msg.get_clip_saved_successfully_message("klip_bez_czasu")],
    #     )
    #
    #     clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
    #     for clip in clips:
    #         clip.duration = None
    #     response = msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME)
    #     await self.expect_command_result_contains('/mojeklipy', [response])
