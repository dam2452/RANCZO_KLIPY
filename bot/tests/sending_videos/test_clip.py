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
        await self.assert_command_result_file_matches(
            await self.send_command('/klip geniusz'),
            "clip_geniusz.mp4",
        )

    @pytest.mark.asyncio
    async def test_clip_not_found(self):
        await self.expect_command_result_contains(
            '/klip nieistniejący_cytat', [get_no_segments_found_message()],
        )

    @pytest.mark.asyncio
    async def test_no_quote_provided(self):
        await self.expect_command_result_contains(
            '/klip', [get_no_quote_provided_message()],
        )

    # Nie można przetestować, ponieważ API nie pozwala wysyłać wiadomości dłuższych niż 4096 znaków
    # @pytest.mark.asyncio
    # async def test_message_too_long(self):
    #     long_quote = "a" * 5000
    #     await self.expect_command_result_contains(
    #         f'/klip {long_quote}', [get_message_too_long_message()]
    #     )

    # Jak znaleźć cytat, który jest zbyt długi?
    # @pytest.mark.asyncio
    # async def test_clip_duration_exceeds_limit(self):
    #     await self.expect_command_result_contains(
    #         '/klip bardzo_długi_cytat', [get_limit_exceeded_clip_duration_message()]
    #     )

    # Nie można przetestować, ponieważ API nie pozwala wysyłać wiadomości dłuższych niż 4096 znaków
    # @pytest.mark.asyncio
    # async def test_user_without_permissions(self):
    #     await DatabaseManager.remove_admin(s.DEFAULT_ADMIN)
    #     long_quote = "a" * 5000
    #     await self.expect_command_result_contains(
    #         f'/klip {long_quote}', [get_message_too_long_message()]
    #     )
