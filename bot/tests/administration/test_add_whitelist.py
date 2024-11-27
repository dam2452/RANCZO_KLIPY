import pytest

import bot.responses.administration.add_whitelist_handler_responses as add_msg
import bot.responses.administration.remove_whitelist_handler_responses as remove_msg
from bot.tests.base_test import BaseTest


class TestWhitelistCommands(BaseTest):

    @pytest.mark.quick
    def test_add_and_remove_valid_user_whitelist(self):
        self.expect_command_result_contains(
            '/addwhitelist 123456789',
            [add_msg.get_user_added_message("123456789")],
        )
        self.expect_command_result_contains(
            '/removewhitelist 123456789',
            [remove_msg.get_user_removed_message("123456789")],
        )

    @pytest.mark.quick
    def test_add_nonexistent_user_whitelist(self):
        self.expect_command_result_contains(
            '/addwhitelist 999999999',
            [add_msg.get_user_added_message("999999999")],
        )
        self.expect_command_result_contains(
            '/removewhitelist 999999999',
            [remove_msg.get_user_removed_message("999999999")],
        )

    @pytest.mark.long
    def test_add_whitelist_invalid_user_id_format(self):
        self.expect_command_result_contains(
            '/addwhitelist user123',
            [add_msg.get_no_user_id_provided_message()],
        )

    @pytest.mark.long
    def test_remove_nonexistent_user_whitelist(self):
        self.expect_command_result_contains(
            '/removewhitelist 888888888',
            [remove_msg.get_user_removed_message("888888888")],
        )
