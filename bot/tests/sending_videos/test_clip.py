import pytest

from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestClipHandler(BaseTest):
    @pytest.mark.quick
    async def test_clip_geniusz(self):
        self.assert_video_matches(await self.send_command('/klip geniusz'), 'geniusz.mp4')
