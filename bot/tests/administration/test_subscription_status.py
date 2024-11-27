from datetime import date

import pytest

import bot.responses.administration.subscription_status_handler_responses as msg
from bot.tests.base_test import BaseTest


class TestSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_subscription_with_active_subscription(self):
        self.send_command('/removesubscription 2015344951')
        self.expect_command_result_contains(
            '/addsubscription 2015344951 30',
            ["Subskrypcja dla użytkownika 2015344951 przedłużona do"],
        )

        self.expect_command_result_contains(
            '/subskrypcja',
            [msg.format_subscription_status_response("2015344951", date(2024, 12, 27), 30)],
        )
        self.send_command('/removesubscription 2015344951')

    @pytest.mark.quick
    def test_subscription_without_subscription(self):
        self.send_command('/removesubscription 2015344951')
        self.expect_command_result_contains(
            '/subskrypcja',
            [msg.get_no_subscription_message()],
        )
