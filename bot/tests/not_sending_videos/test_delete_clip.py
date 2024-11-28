import pytest

import bot.responses.not_sending_videos.delete_clip_handler_responses as delete_msg
import bot.responses.not_sending_videos.save_clip_handler_responses as save_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestDeleteClipCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_delete_existing_clip(self):
        await self.send_command('/klip cytat')
        await self.expect_command_result_contains(
            '/zapisz test_clip',
            [save_msg.get_clip_saved_successfully_message("test_clip")],
        )
        await self.expect_command_result_contains(
            '/usunklip 1',
            [delete_msg.get_clip_deleted_message("test_clip")],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_delete_nonexistent_clip(self):
        await self.expect_command_result_contains(
            '/usunklip 1337',
            [delete_msg.get_clip_not_exist_message(1337)],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_delete_multiple_clips(self):
        for idx, clip_name in enumerate(["pierwszy_clip", "drugi_clip"], start=1):
            await self.send_command(f'/klip {clip_name}')
            await self.expect_command_result_contains(
                f'/zapisz {clip_name}',
                [save_msg.get_clip_saved_successfully_message(clip_name)],
            )

        for idx, clip_name in enumerate(["pierwszy_clip", "drugi_clip"], start=1):
            await self.expect_command_result_contains(
                f'/usunklip {idx}',
                [delete_msg.get_clip_deleted_message(clip_name)],
            )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_delete_clip_with_special_characters(self):
        special_clip_name = "spec@l_clip!"
        await self.send_command('/klip cytat specjalny')
        await self.expect_command_result_contains(
            f'/zapisz {special_clip_name}',
            [save_msg.get_clip_saved_successfully_message(special_clip_name)],
        )
        await self.expect_command_result_contains(
            '/usunklip 1',
            [delete_msg.get_clip_deleted_message(special_clip_name)],
        )
