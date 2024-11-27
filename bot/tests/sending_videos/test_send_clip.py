import pytest

from bot.tests.base_test import BaseTest


class TestSendClipCommand(BaseTest):

    @pytest.mark.quick
    def test_send_existing_clip(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains('/zapisz klip1', ["✅ Klip 'klip1' został zapisany pomyślnie. ✅"])
        self.assert_video_matches(self.send_command('/wyslij klip1'), 'geniusz_clip_sent.mp4')
        self.send_command('/usunklip 1')

    @pytest.mark.quick
    def test_send_nonexistent_clip(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains('/zapisz klip1', ["✅ Klip 'klip1' został zapisany pomyślnie. ✅"])
        self.expect_command_result_contains('/wyslij klip1337', ["Nie znaleziono klipu o numerze"])
        self.send_command('/usunklip 1')

    @pytest.mark.quick
    def test_send_clip_with_no_saved_clips(self):
        self.expect_command_result_contains('/wyslij klip1', ["Nie znaleziono klipu o numerze"])

    @pytest.mark.long
    def test_send_multiple_clips_in_sequence(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains('/zapisz klip1', ["✅ Klip 'klip1' został zapisany pomyślnie. ✅"])
        self.send_command('/klip kozioł')
        self.expect_command_result_contains('/zapisz klip2', ["✅ Klip 'klip2' został zapisany pomyślnie. ✅"])

        self.assert_video_matches(self.send_command('/wyslij klip1'), 'geniusz_clip_sent.mp4')
        self.assert_video_matches(self.send_command('/wyslij klip2'), 'kozioł_clip_sent.mp4')

        self.send_command('/usunklip 1')
        self.send_command('/usunklip 1')

    @pytest.mark.long
    def test_send_clip_with_special_characters_in_name(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains('/zapisz klip@specjalny!', ["✅ Klip 'klip@specjalny!' został zapisany pomyślnie. ✅"])
        self.assert_video_matches(self.send_command('/wyslij klip@specjalny!'), 'geniusz_clip_special_name_sent.mp4')
        self.send_command('/usunklip 1')
