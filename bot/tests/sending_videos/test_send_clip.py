import pytest

from bot.tests.base_test import BaseTest


class TestSendClipCommand(BaseTest):

    @pytest.mark.quick
    def test_send_existing_clip(self):
        self.send_command('/klip geniusz')
        self.send_command('/zapisz klip1')

        send_response = self.send_command('/wyslij klip1')
        self.assert_video_matches(send_response, 'geniusz_clip_sent.mp4')

        self.send_command('/usunklip 1')

    @pytest.mark.quick
    def test_send_nonexistent_clip(self):
        self.send_command('/klip geniusz')
        self.send_command('/zapisz klip1')

        send_response = self.send_command('/wyslij klip1337')
        self.assert_response_contains(send_response, ["Nie znaleziono klipu o numerze"])

        self.send_command('/usunklip 1')

    @pytest.mark.quick
    def test_send_clip_with_no_saved_clips(self):
        send_response = self.send_command('/wyslij klip1')
        self.assert_response_contains(send_response, ["Nie znaleziono klipu o numerze"])

    @pytest.mark.long
    def test_send_multiple_clips_in_sequence(self):
        self.send_command('/klip geniusz')
        self.send_command('/zapisz klip1')
        self.send_command('/klip kozioł')
        self.send_command('/zapisz klip2')

        send_response_1 = self.send_command('/wyslij klip1')
        self.assert_video_matches(send_response_1, 'geniusz_clip_sent.mp4')

        send_response_2 = self.send_command('/wyslij klip2')
        self.assert_video_matches(send_response_2, 'kozioł_clip_sent.mp4')

        self.send_command('/usunklip 1')
        self.send_command('/usunklip 1')

    @pytest.mark.long
    def test_send_clip_with_special_characters_in_name(self):
        self.send_command('/klip geniusz')
        self.send_command('/zapisz klip@specjalny!')

        send_response = self.send_command('/wyslij klip@specjalny!')
        self.assert_video_matches(send_response, 'geniusz_clip_special_name_sent.mp4')

        self.send_command('/usunklip 1')
