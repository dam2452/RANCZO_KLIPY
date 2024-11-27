import pytest

import bot.responses.administration.report_issue_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestReportCommand(BaseTest):

    @pytest.mark.quick
    def test_report_with_valid_message(self):
        self.expect_command_result_contains(
            '/report To i to nie działa',
            [msg.get_report_received_message()],
        )

    @pytest.mark.quick
    def test_report_with_empty_message(self):
        self.expect_command_result_contains(
            '/report',
            [msg.get_no_report_content_message()],
        )

    @pytest.mark.long
    def test_report_with_special_characters_in_message(self):
        self.expect_command_result_contains(
            '/report To się nie działa @#$%^&*()!',
            [msg.get_report_received_message()],
        )

    @pytest.mark.long
    def test_report_with_long_message(self):
        long_message = "To i to nie działa. " * 20
        self.expect_command_result_contains(
            f'/report {long_message}',
            [msg.get_report_received_message()],
        )
