import pytest

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.responses.bot_message_handler_responses import get_response
import bot.responses.not_sending_videos.my_clips_handler_responses as myclips_msg
from bot.settings import settings as sb
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSaveClipHandler(BaseTest):

    @pytest.mark.asyncio
    async def test_save_clip_valid_name(self):
        clip_name = "traktor"
        await self.send_command("/klip geniusz")
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [
                await get_response(
                    RK.CLIP_SAVED_SUCCESSFULLY,
                    self.get_tested_handler_name(),
                    args=[clip_name],
                ),
            ],
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
            [
                await get_response(
                    RK.CLIP_NAME_NOT_PROVIDED,
                    self.get_tested_handler_name(),
                ),
            ],
        )

    @pytest.mark.asyncio
    async def test_save_clip_special_characters_in_name(self):
        clip_name = "traktor@#!$"
        await self.send_command("/klip geniusz")
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [
                await get_response(
                    RK.CLIP_SAVED_SUCCESSFULLY,
                    self.get_tested_handler_name(),
                    args=[clip_name],
                ),
            ],
        )
        clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
        await self.expect_command_result_contains(
            '/mojeklipy',
            [self.remove_n_lines(myclips_msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME), 4)],
        )

    @pytest.mark.asyncio
    async def test_save_clip_duplicate_name(self):
        clip_name = "traktor"
        await self.send_command(f"/klip geniusz")
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [
                await get_response(
                    RK.CLIP_SAVED_SUCCESSFULLY,
                    self.get_tested_handler_name(),
                    args=[clip_name],
                ),
            ],
        )
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [
                await get_response(
                    RK.CLIP_NAME_EXISTS,
                    self.get_tested_handler_name(),
                    args=[clip_name],
                ),
            ],
        )

    @pytest.mark.asyncio
    async def test_save_clip_no_segment_selected(self):
        response = await self.send_command('/zapisz klip_bez_segmentu')
        self.assert_response_contains(
            response,
            [
                await get_response(
                    RK.NO_SEGMENT_SELECTED,
                    self.get_tested_handler_name(),
                ),
            ],
        )

    @pytest.mark.asyncio
    async def test_save_clip_name_length_exceeded(self):
        long_name = "a" * (sb.MAX_CLIP_NAME_LENGTH + 1)
        response = await self.send_command(f'/zapisz {long_name}')
        self.assert_response_contains(
            response,
            [
                await get_response(
                    RK.CLIP_NAME_LENGTH_EXCEEDED,
                    self.get_tested_handler_name(),
                ),
            ],
        )
