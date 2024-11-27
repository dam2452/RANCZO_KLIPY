import pytest

import bot.responses.administration.remove_subscription_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestRemoveSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_remove_existing_subscription(self):
        self.expect_command_result_contains(
            '/addsubscription 2015344951 30',
            ["Subskrypcja dla użytkownika 2015344951"],
        )
        self.expect_command_result_contains(
            '/removesubscription 2015344951',
            [msg.get_subscription_removed_message("2015344951")],
        )

    @pytest.mark.quick
    def test_remove_nonexistent_subscription(self):
        self.expect_command_result_contains(
            '/removesubscription 987654321',
            [msg.get_subscription_removed_message("987654321")],
        )

    @pytest.mark.long
    def test_remove_subscription_twice(self):
        self.expect_command_result_contains(
            '/addsubscription 2015344951 30',
            ["Subskrypcja dla użytkownika 2015344951"],
        )
        self.expect_command_result_contains(
            '/removesubscription 2015344951',
            [msg.get_subscription_removed_message("2015344951")],
        )
        self.expect_command_result_contains(
            '/removesubscription 2015344951',
            [msg.get_subscription_removed_message("2015344951")],
        )

    @pytest.mark.long
    def test_remove_subscription_invalid_user_id_format(self):
        self.expect_command_result_contains(
            '/removesubscription user123',
            [msg.get_subscription_removed_message("user123")],
        )
