import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.not_sending_videos.my_clips_handler_responses as myclips_msg
import bot.responses.not_sending_videos.save_clip_handler_responses as save_msg
from bot.settings import settings as sb
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestClipSaveCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_save_clip_valid_name(self):
        clip_name = "traktor"
        await self.send_command("/klip geniusz")
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [save_msg.get_clip_saved_successfully_message(clip_name)],
        )
        clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
        await self.expect_command_result_contains(
            '/mojeklipy',
            [self.remove_n_lines(myclips_msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME), 4)],
        )

    @pytest.mark.asyncio
    async def test_save_clip_without_name(self):
        await self.expect_command_result_contains(
            '/zapisz',
            [save_msg.get_clip_name_not_provided_message()],
        )

    @pytest.mark.asyncio
    async def test_save_clip_special_characters_in_name(self):
        clip_name = "traktor@#!$"
        await self.send_command("/klip geniusz")
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [save_msg.get_clip_saved_successfully_message(clip_name)],
        )
        clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
        await self.expect_command_result_contains(
            '/mojeklipy',
            [self.remove_n_lines(myclips_msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME), 4)],
        )

    @pytest.mark.asyncio
    async def test_save_clip_duplicate_name(self):
        # pylint: disable=f-string-without-interpolation
        clip_name = "traktor"
        await self.send_command(f"/klip geniusz")
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [save_msg.get_clip_saved_successfully_message(clip_name)],
        )
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [save_msg.get_clip_name_exists_message(clip_name)],
        )
        # pylint: enable=f-string-without-interpolation

    @pytest.mark.asyncio
    async def test_save_clip_no_segment_selected(self):
        response = await self.send_command('/zapisz klip_bez_segmentu')
        self.assert_response_contains(response, [save_msg.get_no_segment_selected_message()])

    @pytest.mark.asyncio
    async def test_save_clip_name_length_exceeded(self):
        long_name = "a" * (sb.MAX_CLIP_NAME_LENGTH + 1)
        response = await self.send_command(f'/zapisz {long_name}')
        self.assert_response_contains(response, [save_msg.get_clip_name_length_exceeded_message()])
