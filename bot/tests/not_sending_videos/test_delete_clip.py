import pytest

import bot.responses.not_sending_videos.delete_clip_handler_responses as delete_msg
from bot.tests.base_test import BaseTest


class TestDeleteClipCommand(BaseTest):

    @pytest.mark.quick
    def test_delete_existing_clip(self):
        self.send_command('/klip cytat')
        self.expect_command_result_contains(
            '/zapisz test_clip',
            [delete_msg.get_clip_deleted_message("test_clip")],
        )
        self.expect_command_result_contains(
            '/usunklip 1',
            [delete_msg.get_clip_deleted_message("test_clip")],
        )

    @pytest.mark.quick
    def test_delete_nonexistent_clip(self):
        self.expect_command_result_contains(
            '/usunklip 1337',
            [delete_msg.get_clip_not_exist_message(1337)],
        )

    @pytest.mark.long
    def test_delete_multiple_clips(self):
        self.send_command('/klip pierwszy')
        self.expect_command_result_contains(
            '/zapisz pierwszy_clip',
            [delete_msg.get_clip_deleted_message("pierwszy_clip")],
        )

        self.send_command('/klip drugi')
        self.expect_command_result_contains(
            '/zapisz drugi_clip',
            [delete_msg.get_clip_deleted_message("drugi_clip")],
        )

        self.expect_command_result_contains(
            '/usunklip 1',
            [delete_msg.get_clip_deleted_message("pierwszy_clip")],
        )
        self.expect_command_result_contains(
            '/usunklip 1',
            [delete_msg.get_clip_deleted_message("drugi_clip")],
        )

    @pytest.mark.long
    def test_delete_clip_with_special_characters(self):
        self.send_command('/klip cytat specjalny')
        self.expect_command_result_contains(
            '/zapisz spec@l_clip!',
            [delete_msg.get_clip_deleted_message("spec@l_clip!")],
        )
        self.expect_command_result_contains(
            '/usunklip 1',
            [delete_msg.get_clip_deleted_message("spec@l_clip!")],
        )
