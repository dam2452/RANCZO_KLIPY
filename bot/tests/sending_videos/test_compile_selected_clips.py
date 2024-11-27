import pytest

from bot.tests.base_test import BaseTest


class TestMergeClipsCommand(BaseTest):

    @pytest.mark.quick
    def test_merge_multiple_clips(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains('/zapisz klip1', ["✅ Klip 'klip1' został zapisany pomyślnie. ✅"])
        self.send_command('/klip kozioł')
        self.expect_command_result_contains('/zapisz klip2', ["✅ Klip 'klip2' został zapisany pomyślnie. ✅"])
        self.send_command('/klip uczniowie')
        self.expect_command_result_contains('/zapisz klip3', ["✅ Klip 'klip3' został zapisany pomyślnie. ✅"])

        self.assert_video_matches(self.send_command('/polaczklipy 1 2 3'), 'merged_clip_1_2_3.mp4')

        self.send_command('/usunklip 1')
        self.send_command('/usunklip 1')
        self.send_command('/usunklip 1')

    @pytest.mark.quick
    def test_merge_invalid_clip_numbers(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains('/zapisz klip1', ["✅ Klip 'klip1' został zapisany pomyślnie. ✅"])
        self.send_command('/klip kozioł')
        self.expect_command_result_contains('/zapisz klip2', ["✅ Klip 'klip2' został zapisany pomyślnie. ✅"])

        self.expect_command_result_contains(
            '/polaczklipy 1 5',
            ["📄 Podaj numery klipów do skompilowania w odpowiedniej kolejności."]
        )

        self.send_command('/usunklip 1')
        self.send_command('/usunklip 2')

    @pytest.mark.quick
    def test_merge_single_clip(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains('/zapisz klip1', ["✅ Klip 'klip1' został zapisany pomyślnie. ✅"])

        self.assert_video_matches(self.send_command('/polaczklipy 1'), 'merged_single_clip_1.mp4')

        self.send_command('/usunklip 1')

    @pytest.mark.long
    def test_merge_no_clips(self):
        self.expect_command_result_contains(
            '/polaczklipy 1 2',
            ["⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"]
        )

    @pytest.mark.long
    def test_merge_clips_with_special_characters_in_name(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains('/zapisz klip@specjalny!', ["✅ Klip 'klip@specjalny!' został zapisany pomyślnie. ✅"])

        self.assert_video_matches(self.send_command('/polaczklipy 1'), 'merged_special_name_clip.mp4')

        self.send_command('/usunklip 1')
