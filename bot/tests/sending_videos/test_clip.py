import pytest

from bot.responses.sending_videos.clip_handler_responses import (
    get_no_quote_provided_message,
    get_no_segments_found_message,
)
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestClipHandler(BaseTest):
    @pytest.mark.asyncio
    async def test_clip_found(self):
        response = await self.send_command('/klip geniusz')
        await self.assert_command_result_file_matches(response, "clip_geniusz.mp4")

    @pytest.mark.asyncio
    async def test_clip_not_found(self):
        response = await self.send_command('/klip nieistniejący_cytat')
        self.assert_response_contains(response, [get_no_segments_found_message()])

    @pytest.mark.asyncio
    async def test_no_quote_provided(self):
        response = await self.send_command('/klip')
        self.assert_response_contains(response, [get_no_quote_provided_message()])

    # hmm, how to test this becuse api dont let me to send messages longer than 4096 characters
    # @pytest.mark.asyncio
    # async def test_message_too_long(self):
    #     long_quote = "a" * 5000
    #     response = await self.send_command(f'/klip {long_quote}')
    #     self.assert_response_contains(response, [get_message_too_long_message()])

    #how to find a quote that is too long?
    # @pytest.mark.asyncio
    # async def test_clip_duration_exceeds_limit(self):
    #     response = await self.send_command('/klip bardzo_długi_cytat')
    #     self.assert_response_contains(response, [get_limit_exceeded_clip_duration_message()])

    # hmm, how to test this becuse api dont let me to send messages longer than 4096 characters
    # @pytest.mark.asyncio
    # async def test_user_without_permissions(self):
    #     await DatabaseManager.remove_admin(s.DEFAULT_ADMIN)
    #     long_quote = "a" * 5000
    #     response = await self.send_command(f'/klip {long_quote}')
    #     self.assert_response_contains(response, [get_message_too_long_message()])
