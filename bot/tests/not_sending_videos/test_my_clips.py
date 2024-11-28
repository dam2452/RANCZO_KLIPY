import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.not_sending_videos.my_clips_handler_responses as myclips_msg
import bot.responses.not_sending_videos.save_clip_handler_responses as save_msg
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestMyClipsCommand(BaseTest):
    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_myclips_no_clips(self):
        await self.expect_command_result_contains(
            '/mojeklipy',
            [myclips_msg.get_no_saved_clips_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_myclips_with_clips(self):

        await self.send_command("/klip świnia")
        await self.expect_command_result_contains(
            '/zapisz nazwa',
            [save_msg.get_clip_saved_successfully_message("nazwa")],
        )


        clips = await DatabaseManager.get_saved_clips(s.DEFAULT_ADMIN)
        response = myclips_msg.format_myclips_response(clips, s.ADMIN_USERNAME, s.ADMIN_FULL_NAME)

        await self.expect_command_result_contains('/mojeklipy', [response])
