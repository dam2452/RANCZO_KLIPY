import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.not_sending_videos.my_clips_handler_responses as myclips_msg
import bot.responses.not_sending_videos.save_clip_handler_responses as msg
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestClipSaveCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_save_clip_valid_name(self):
        clip_name = "traktor"
        await self.send_command(f"/klip {clip_name}")
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [msg.get_clip_saved_successfully_message(clip_name)],
        )
        clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
        await self.expect_command_result_contains(
            '/mojeklipy',
            [myclips_msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME)],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_save_clip_without_name(self):
        await self.expect_command_result_contains(
            '/zapisz',
            [msg.get_clip_name_not_provided_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_save_clip_special_characters_in_name(self):
        clip_name = "traktor@#!$"
        await self.send_command("/klip traktor")
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [msg.get_clip_saved_successfully_message(clip_name)],
        )
        clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
        await self.expect_command_result_contains(
            '/mojeklipy',
            [myclips_msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME)],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_save_clip_duplicate_name(self):
        clip_name = "traktor"
        await self.send_command(f"/klip {clip_name}")
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [msg.get_clip_saved_successfully_message(clip_name)],
        )
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [msg.get_clip_name_exists_message(clip_name)],
        )
