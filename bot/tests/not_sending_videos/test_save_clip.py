import pytest

import bot.responses.not_sending_videos.save_clip_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestClipSaveCommand(BaseTest):

    @pytest.mark.quick
    def test_save_clip_valid_name(self):
        self.send_command("/klip traktor")
        self.expect_command_result_contains(
            '/zapisz traktor',
            [msg.get_clip_saved_successfully_message("traktor")],
        )
        self.expect_command_result_contains('/mojeklipy', ["traktor"])
        self.send_command("/usunklip 1")

    @pytest.mark.quick
    def test_save_clip_without_name(self):
        self.expect_command_result_contains(
            '/zapisz',
            [msg.get_clip_name_not_provided_message()],
        )

    @pytest.mark.long
    def test_save_clip_special_characters_in_name(self):
        self.send_command("/klip traktor")
        self.expect_command_result_contains(
            '/zapisz traktor@#!$',
            [msg.get_clip_saved_successfully_message("traktor@#!$")],
        )
        self.expect_command_result_contains('/mojeklipy', ["traktor@#!$"])
        self.send_command("/usunklip 1")

    @pytest.mark.long
    def test_save_clip_duplicate_name(self):
        self.send_command("/klip traktor")
        self.expect_command_result_contains(
            '/zapisz traktor',
            [msg.get_clip_saved_successfully_message("traktor")],
        )
        self.expect_command_result_contains(
            '/zapisz traktor',
            [msg.get_clip_name_exists_message("traktor")],
        )
        self.send_command("/usunklip 1")
