import pytest

from bot.tests.base_test import BaseTest


class TestAdjustClipCommand(BaseTest):

    @pytest.mark.quick
    def test_adjust_clip_with_two_params(self):
        clip_response = self.send_command('/klip geniusz')
        self.assert_video_matches(clip_response, 'geniusz.mp4')

        adjust_response = self.send_command('/dostosuj -5.5 1.5')
        self.assert_video_matches(adjust_response, 'geniusz_adjusted_-5.5_1.5.mp4')

    @pytest.mark.quick
    def test_adjust_clip_with_three_params(self):
        search_response = self.send_command('/szukaj kozioł')
        self.assert_response_contains(search_response, ["Wyniki wyszukiwania"])

        select_response = self.send_command('/wybierz 1')
        self.assert_video_matches(select_response, 'kozioł_clip_1.mp4')

        adjust_response = self.send_command('/dostosuj 1 10.0 -3')
        self.assert_video_matches(adjust_response, 'kozioł_adjusted_10.0_-3.mp4')

    @pytest.mark.long
    def test_adjust_clip_with_invalid_time_format(self):
        clip_response = self.send_command('/klip geniusz')
        self.assert_video_matches(clip_response, 'geniusz.mp4')

        adjust_response = self.send_command('/dostosuj -abc 1.2')
        self.assert_response_contains(
            adjust_response, [
                "📝 Podaj czas w formacie `<float> <float>` lub"
                " `<index> <float> <float>`. Przykład: /dostosuj 10.5 -15.2 lub"
                " /dostosuj 1 10.5 -15.2",
            ],
        )

    @pytest.mark.long
    def test_adjust_nonexistent_clip_number(self):
        search_response = self.send_command('/szukaj kozioł')
        self.assert_response_contains(search_response, ["Wyniki wyszukiwania"])

        adjust_response = self.send_command('/dostosuj 99999 10.0 -3')
        self.assert_response_contains(adjust_response, ["⚠️ Podano nieprawidłowy indeks cytatu.⚠️"])

    @pytest.mark.long
    def test_adjust_clip_with_large_extension_values(self):
        clip_response = self.send_command('/klip geniusz')
        self.assert_video_matches(clip_response, 'geniusz.mp4')

        adjust_response = self.send_command('/dostosuj 50 50')
        self.assert_video_matches(adjust_response, 'geniusz_adjusted_50_50.mp4')
