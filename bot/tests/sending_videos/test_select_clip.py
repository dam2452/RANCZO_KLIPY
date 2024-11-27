import pytest

from bot.tests.base_test import BaseTest


class TestSelectClipCommand(BaseTest):

    @pytest.mark.quick
    def test_select_existing_clip(self):
        self.expect_command_result_contains('/szukaj kozioł', ["Wyniki wyszukiwania"])
        self.assert_video_matches(self.send_command('/wybierz 1'), 'kozioł_clip_1.mp4')

    @pytest.mark.quick
    def test_select_nonexistent_clip(self):
        self.expect_command_result_contains('/szukaj Anglii', ["Wyniki wyszukiwania"])
        self.expect_command_result_contains('/wybierz 100', ["❌ Nieprawidłowy numer cytatu.❌"])

    @pytest.mark.long
    def test_select_multiple_clips_in_sequence(self):
        self.expect_command_result_contains('/szukaj kozioł', ["Wyniki wyszukiwania"])
        self.assert_video_matches(self.send_command('/wybierz 1'), 'kozioł_clip_select_1.mp4')
        self.assert_video_matches(self.send_command('/wybierz 2'), 'kozioł_clip_select_2.mp4')
