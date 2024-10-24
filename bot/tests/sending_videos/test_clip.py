import pytest

from bot.tests.base_test import BaseTest


class TestClipHandler(BaseTest):
    @pytest.mark.quick
    def test_clip_geniusz(self):
        response = self.send_command('/klip geniusz')
        self.assert_video_matches(response, 'geniusz.mp4')
