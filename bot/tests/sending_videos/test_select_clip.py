import pytest

from bot.tests.base_test import BaseTest


class TestSelectClipCommand(BaseTest):

    @pytest.mark.quick
    def test_select_existing_clip(self):
        search_response = self.send_command('/szukaj kozioł')
        self.assert_response_contains(search_response, ["Wyniki wyszukiwania"])

        select_response = self.send_command('/wybierz 1')
        self.assert_video_matches(select_response, 'kozioł_clip_1.mp4')

    @pytest.mark.quick
    def test_select_nonexistent_clip(self):
        search_response = self.send_command('/szukaj Anglii')
        self.assert_response_contains(search_response, ["Wyniki wyszukiwania"])

        select_response = self.send_command('/wybierz 100')
        self.assert_response_contains(select_response, ["❌ Nieprawidłowy numer cytatu.❌"])

    @pytest.mark.long
    def test_select_multiple_clips_in_sequence(self):
        search_response = self.send_command('/szukaj kozioł')
        self.assert_response_contains(search_response, ["Wyniki wyszukiwania"])

        select_response_1 = self.send_command('/wybierz 1')
        self.assert_video_matches(select_response_1, 'kozioł_clip_select_1.mp4')

        select_response_2 = self.send_command('/wybierz 2')
        self.assert_video_matches(select_response_2, 'kozioł_clip_select_2.mp4')
