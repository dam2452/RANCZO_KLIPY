import pytest

from bot.tests.base_test import BaseTest


class TestCompileClipsCommand(BaseTest):

    @pytest.mark.quick
    def test_compile_all_clips(self):
        search_response = self.send_command('/szukaj Anglii')
        self.assert_response_contains(search_response, ["Wyniki wyszukiwania"])

        compile_response = self.send_command('/kompiluj wszystko', timeout=30)
        self.assert_video_matches(compile_response, 'Anglii_compilation_all.mp4')

    @pytest.mark.quick
    def test_compile_clip_range(self):
        search_response = self.send_command('/szukaj kozioł')
        self.assert_response_contains(search_response, ["Wyniki wyszukiwania"])

        compile_response = self.send_command('/kompiluj 1-4')
        self.assert_video_matches(compile_response, 'kozioł_compilation_1-4.mp4')

    @pytest.mark.quick
    def test_compile_specific_clips(self):
        search_response = self.send_command('/szukaj kozioł')
        self.assert_response_contains(search_response, ["Wyniki wyszukiwania"])

        compile_response = self.send_command('/kompiluj 1 3 5')
        self.assert_video_matches(compile_response, 'kozioł_compilation_1_3_5.mp4')

    @pytest.mark.long
    def test_compile_out_of_range_clips(self):
        search_response = self.send_command('/szukaj kozioł')
        self.assert_response_contains(search_response, ["Wyniki wyszukiwania"])

        compile_response = self.send_command('/kompiluj 10000-10005')
        self.assert_response_contains(compile_response, ["⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"])

    @pytest.mark.long
    def test_compile_invalid_clip_numbers(self):
        search_response = self.send_command('/szukaj kozioł')
        self.assert_response_contains(search_response, ["Wyniki wyszukiwania"])

        compile_response = self.send_command('/kompiluj 1 abc 3')
        self.assert_video_matches(compile_response, 'kozioł_compilation_1_abc_3.mp4')
