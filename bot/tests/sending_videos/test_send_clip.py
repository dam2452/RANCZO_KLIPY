import pytest

import bot.responses.not_sending_videos.save_clip_handler_responses as save_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSendClipCommand(BaseTest):

    # @pytest.mark.asyncio
    # async def test_send_existing_clip_by_number(self):
    #     clip_name = "klip1"
    #     await self.send_command('/klip geniusz')
    #     await self.expect_command_result_contains(
    #         f'/zapisz {clip_name}',
    #         [save_msg.get_clip_saved_successfully_message(clip_name)],
    #     )
    #
    #     response = await self.send_command('/wyslij 1',timeout=30)
    #     await self.assert_command_result_file_matches(
    #         response, 'send_clip_geniusz_klip1.mp4'
    #     )

    @pytest.mark.asyncio
    async def test_send_existing_clip_by_name(self):
        clip_name = "klip_geniusz"
        await self.send_command('/klip geniusz')
        await self.expect_command_result_contains(
            f'/zapisz {clip_name}',
            [save_msg.get_clip_saved_successfully_message(clip_name)],
        )

        response = await self.send_command(f'/wyslij {clip_name}')
        await self.assert_command_result_file_matches(
            response, 'send_clip_geniusz_klip1.mp4',
        )

    # @pytest.mark.asyncio
    # async def test_send_nonexistent_clip(self):
    #     clip_number = 1
    #     response = await self.send_command(f'/wyslij {clip_number}')
    #     self.assert_response_contains(
    #         response, [msg.get_clip_not_found_message(clip_number)]
    #     )

    @pytest.mark.asyncio
    async def test_send_clip_with_special_characters_in_name(self):

        special_clip_name = "klip@specjalny!"
        await self.send_command('/klip geniusz')
        await self.expect_command_result_contains(
            f'/zapisz {special_clip_name}',
            [save_msg.get_clip_saved_successfully_message(special_clip_name)],
        )

        response = await self.send_command(f'/wyslij {special_clip_name}')
        await self.assert_command_result_file_matches(
            response, 'send_clip_geniusz_special_name.mp4',
        )

    # @pytest.mark.asyncio
    # async def test_send_clip_duration_exceeds_limit(self):
    #     clip_name = "klip_dlugi"
    #     await self.send_command('/klip dlugi')
    #     await self.expect_command_result_contains(
    #         f'/zapisz {clip_name}',
    #         [save_msg.get_clip_saved_successfully_message(clip_name)],
    #     )
    #
    #     response = await self.send_command(f'/wyslij {clip_name}')
    #     self.assert_response_contains(
    #         response, [msg.get_limit_exceeded_clip_duration_message()]
    #     )
