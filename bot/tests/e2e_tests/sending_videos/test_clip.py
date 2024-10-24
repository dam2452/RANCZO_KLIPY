from bot.tests.e2e_tests.base_test import BaseE2ETest


class TestClipHandler(BaseE2ETest):

    def test_clip_geniusz(self):
        response = self.send_command('/klip geniusz')
        self.assert_video_matches(response, 'geniusz.mp4')
