import pytest

from bot.tests.base_test import BaseTest


class TestManualClipCommand(BaseTest):

    @pytest.mark.quick
    def test_cut_clip_valid_range(self):
        cut_response = self.send_command('/wytnij S07E06 36:47.50 36:49.00')
        self.assert_video_matches(cut_response, 'cut_S07E06_36-47.50_36-49.00.mp4')

    @pytest.mark.quick
    def test_cut_clip_invalid_time_format(self):
        cut_response = self.send_command('/wytnij S07E06 abc 36:49.00')
        self.assert_response_contains(cut_response, ["❌ Błędny format czasu! Użyj formatu"])

    @pytest.mark.quick
    def test_cut_clip_nonexistent_episode(self):
        cut_response = self.send_command('/wytnij S99E99 00:00.00 00:10.00')
        self.assert_response_contains(cut_response, ["❌ Nie znaleziono pliku wideo dla podanego sezonu i odcinka."])

    @pytest.mark.long
    def test_cut_clip_end_time_before_start_time(self):
        cut_response = self.send_command('/wytnij S07E06 36:49.00 36:47.50')
        self.assert_response_contains(cut_response, ["❌ Czas zakończenia musi być późniejszy niż czas rozpoczęcia!"])

    @pytest.mark.long
    def test_cut_clip_large_time_range(self):
        cut_response = self.send_command('/wytnij S07E06 40:00.00 41:00.00', timeout=30)
        self.assert_video_matches(cut_response, 'cut_S07E06_40-00.00_41-00.00.mp4')

    @pytest.mark.long
    def test_cut_clip_exact_episode_length(self):
        cut_response = self.send_command('/wytnij S07E06 00:00.00 45:00.00', timeout=30)
        self.assert_response_contains(cut_response, ["❌ Wyodrębniony klip jest za duży"])
