import pytest

from bot.tests.base_test import BaseTest


class TestClipHandler(BaseTest):
    @pytest.mark.quick
    def test_clip_geniusz(self):
        self.assert_video_matches(self.send_command('/klip geniusz'), 'geniusz.mp4')
