import pytest

from bot.tests.base_test import BaseTest


class TestMergeClipsCommand(BaseTest):

    @pytest.mark.quick
    def test_merge_multiple_clips(self):
        self.send_command('/klip geniusz')
        self.send_command('/zapisz klip1')
        self.send_command('/klip kozioł')
        self.send_command('/zapisz klip2')
        self.send_command('/klip uczniowie')
        self.send_command('/zapisz klip3')

        merge_response = self.send_command('/polaczklipy 1 2 3')
        self.assert_video_matches(merge_response, 'merged_clip_1_2_3.mp4')

        self.send_command('/usunklip 1')
        self.send_command('/usunklip 1')
        self.send_command('/usunklip 1')

    @pytest.mark.quick
    def test_merge_invalid_clip_numbers(self):
        self.send_command('/klip geniusz')
        self.send_command('/zapisz klip1')
        self.send_command('/klip kozioł')
        self.send_command('/zapisz klip2')

        merge_response = self.send_command('/polaczklipy 1 5')
        self.assert_response_contains(merge_response, ["📄 Podaj numery klipów do skompilowania w odpowiedniej kolejności."])

        self.send_command('/usunklip 1')
        self.send_command('/usunklip 2')

    @pytest.mark.quick
    def test_merge_single_clip(self):
        self.send_command('/klip geniusz')
        self.send_command('/zapisz klip1')

        merge_response = self.send_command('/polaczklipy 1')
        self.assert_video_matches(merge_response, 'merged_single_clip_1.mp4')

        self.send_command('/usunklip 1')

    @pytest.mark.long
    def test_merge_no_clips(self):
        merge_response = self.send_command('/polaczklipy 1 2')
        self.assert_response_contains(merge_response, ["⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"])

    @pytest.mark.long
    def test_merge_clips_with_special_characters_in_name(self):
        self.send_command('/klip geniusz')
        self.send_command('/zapisz klip@specjalny!')

        merge_response = self.send_command('/polaczklipy 1')
        self.assert_video_matches(merge_response, 'merged_special_name_clip.mp4')

        self.send_command('/usunklip 1')
