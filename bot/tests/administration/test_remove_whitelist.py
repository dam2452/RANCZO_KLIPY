import pytest

import bot.responses.administration.remove_whitelist_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestRemoveWhitelistCommand(BaseTest):

    @pytest.mark.quick
    def test_remove_existing_user_whitelist(self):
        self.expect_command_result_contains(
            '/addwhitelist 6967485026',
            ["Dodano", "do whitelisty."],
        )
        self.expect_command_result_contains(
            '/removewhitelist 6967485026',
            [msg.get_user_removed_message("6967485026")],
        )

    @pytest.mark.quick
    def test_remove_nonexistent_user_whitelist(self):
        self.expect_command_result_contains(
            '/removewhitelist 6967485026',
            [msg.get_user_removed_message("6967485026")],
        )

    @pytest.mark.long
    def test_remove_user_whitelist_twice(self):
        self.expect_command_result_contains(
            '/addwhitelist 123456789',
            ["Użytkownik o ID 123456789 został dodany do whitelisty."],
        )
        self.expect_command_result_contains(
            '/removewhitelist 123456789',
            [msg.get_user_removed_message("123456789")],
        )
        self.expect_command_result_contains(
            '/removewhitelist 123456789',
            [msg.get_user_not_in_whitelist_message("123456789")],
        )

    @pytest.mark.long
    def test_remove_whitelist_invalid_user_id_format(self):
        self.expect_command_result_contains(
            '/removewhitelist user123',
            [msg.get_no_user_id_provided_message()],
        )
