import pytest

import bot.responses.sending_videos.adjust_video_clip_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestAdjustClipCommand(BaseTest):

    @pytest.mark.quick
    def test_adjust_clip_with_two_params(self):
        self.assert_video_matches(self.send_command('/klip geniusz'), 'geniusz.mp4')
        self.assert_video_matches(self.send_command('/dostosuj -5.5 1.5'), 'geniusz_adjusted_-5.5_1.5.mp4')

    @pytest.mark.quick
    def test_adjust_clip_with_three_params(self):
        self.expect_command_result_contains('/szukaj kozioł', ["Wyniki wyszukiwania"])
        self.assert_video_matches(self.send_command('/wybierz 1'), 'kozioł_clip_1.mp4')
        self.assert_video_matches(self.send_command('/dostosuj 1 10.0 -3'), 'kozioł_adjusted_10.0_-3.mp4')

    @pytest.mark.long
    def test_adjust_clip_with_invalid_time_format(self):
        self.assert_video_matches(self.send_command('/klip geniusz'), 'geniusz.mp4')
        self.expect_command_result_contains(
            '/dostosuj -abc 1.2',
            [msg.get_invalid_args_count_message()],
        )

    @pytest.mark.long
    def test_adjust_nonexistent_clip_number(self):
        self.expect_command_result_contains('/szukaj kozioł', ["Wyniki wyszukiwania"])
        self.expect_command_result_contains(
            '/dostosuj 99999 10.0 -3',
            [msg.get_invalid_segment_index_message()],
        )

    @pytest.mark.long
    def test_adjust_clip_with_large_extension_values(self):
        self.assert_video_matches(self.send_command('/klip geniusz'), 'geniusz.mp4')
        self.assert_video_matches(self.send_command('/dostosuj 50 50'), 'geniusz_adjusted_50_50.mp4')
