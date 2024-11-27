from datetime import date

import pytest

import bot.responses.administration.add_subscription_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestAddSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_add_subscription_valid_user(self):
        self.expect_command_result_contains(
            '/addsub 2015344951 30',
            [msg.get_subscription_extended_message("2015344951",  date(2024, 12, 27))],
        )

    @pytest.mark.quick
    def test_add_subscription_nonexistent_user(self):
        self.expect_command_result_contains(
            '/addsubscription 999999999 30',
            [msg.get_subscription_error_message()],
        )

    @pytest.mark.long
    def test_add_subscription_invalid_days_format(self):
        self.expect_command_result_contains(
            '/addsubscription 123456789 trzydzieści',
            [msg.get_no_user_id_provided_message()],
        )

    @pytest.mark.long
    def test_add_subscription_invalid_user_id_format(self):
        self.expect_command_result_contains(
            '/addsubscription user123 30',
            [msg.get_no_user_id_provided_message()],
        )

    @pytest.mark.long
    def test_add_subscription_negative_days(self):
        self.expect_command_result_contains(
            '/addsubscription 123456789 -30',
            [msg.get_no_user_id_provided_message()],
        )
