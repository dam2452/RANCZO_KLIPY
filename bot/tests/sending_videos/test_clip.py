import pytest

from bot.database.response_keys import ResponseKey as RK
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestClipHandler(BaseTest):
    @pytest.mark.asyncio
    async def test_clip_found(self):
        quote = "geniusz"
        await self.assert_command_result_file_matches(
            await self.send_command(f'/klip {quote}'),
            f"clip_{quote}.mp4",
        )

    @pytest.mark.asyncio
    async def test_clip_not_found(self):
        await self.expect_command_result_contains(
            '/klip nieistniejący_cytat', [await self.get_response(RK.NO_SEGMENTS_FOUND)],
        )

    @pytest.mark.asyncio
    async def test_no_quote_provided(self):
        await self.expect_command_result_contains(
            '/klip', [await self.get_response(RK.NO_QUOTE_PROVIDED)],
        )
