import pytest

from bot.tests.base_test import BaseTest


class TestCompileClipsCommand(BaseTest):

    @pytest.mark.quick
    def test_compile_all_clips(self):
        self.expect_command_result_contains('/szukaj Anglii', ["Wyniki wyszukiwania"])
        self.assert_video_matches(self.send_command('/kompiluj wszystko', timeout=30), 'Anglii_compilation_all.mp4')

    @pytest.mark.quick
    def test_compile_clip_range(self):
        self.expect_command_result_contains('/szukaj kozioł', ["Wyniki wyszukiwania"])
        self.assert_video_matches(self.send_command('/kompiluj 1-4'), 'kozioł_compilation_1-4.mp4')

    @pytest.mark.quick
    def test_compile_specific_clips(self):
        self.expect_command_result_contains('/szukaj kozioł', ["Wyniki wyszukiwania"])
        self.assert_video_matches(self.send_command('/kompiluj 1 3 5'), 'kozioł_compilation_1_3_5.mp4')

    @pytest.mark.long
    def test_compile_out_of_range_clips(self):
        self.expect_command_result_contains('/szukaj kozioł', ["Wyniki wyszukiwania"])
        self.expect_command_result_contains(
            '/kompiluj 10000-10005',
            ["⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"]
        )

    @pytest.mark.long
    def test_compile_invalid_clip_numbers(self):
        self.expect_command_result_contains('/szukaj kozioł', ["Wyniki wyszukiwania"])
        self.assert_video_matches(self.send_command('/kompiluj 1 abc 3'), 'kozioł_compilation_1_abc_3.mp4')
