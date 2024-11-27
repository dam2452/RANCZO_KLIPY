import pytest

import bot.responses.not_sending_videos.save_clip_handler_responses as save_msg
from bot.tests.base_test import BaseTest


class TestSendClipCommand(BaseTest):

    @pytest.mark.quick
    def test_send_existing_clip(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains(
            '/zapisz klip1',
            [save_msg.get_clip_saved_successfully_message("klip1")],
        )
        self.assert_video_matches(self.send_command('/wyslij klip1'), 'geniusz_clip_sent.mp4')
        self.send_command('/usunklip 1')

    @pytest.mark.quick
    def test_send_nonexistent_clip(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains(
            '/zapisz klip1',
            [save_msg.get_clip_saved_successfully_message("klip1")],
        )
        self.expect_command_result_contains(
            '/wyslij klip1337',
            [save_msg.get_clip_name_not_provided_message()],
        )
        self.send_command('/usunklip 1')

    @pytest.mark.quick
    def test_send_clip_with_no_saved_clips(self):
        self.expect_command_result_contains(
            '/wyslij klip1',
            [save_msg.get_clip_name_not_provided_message()],
        )

    @pytest.mark.long
    def test_send_multiple_clips_in_sequence(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains(
            '/zapisz klip1',
            [save_msg.get_clip_saved_successfully_message("klip1")],
        )
        self.send_command('/klip kozioł')
        self.expect_command_result_contains(
            '/zapisz klip2',
            [save_msg.get_clip_saved_successfully_message("klip2")],
        )

        self.assert_video_matches(self.send_command('/wyslij klip1'), 'geniusz_clip_sent.mp4')
        self.assert_video_matches(self.send_command('/wyslij klip2'), 'kozioł_clip_sent.mp4')

        self.send_command('/usunklip 1')
        self.send_command('/usunklip 2')

    @pytest.mark.long
    def test_send_clip_with_special_characters_in_name(self):
        self.send_command('/klip geniusz')
        self.expect_command_result_contains(
            '/zapisz klip@specjalny!',
            [save_msg.get_clip_saved_successfully_message("klip@specjalny!")],
        )
        self.assert_video_matches(self.send_command('/wyslij klip@specjalny!'), 'geniusz_clip_special_name_sent.mp4')
        self.send_command('/usunklip 1')
