import pytest

from bot.tests.base_test import BaseTest


class TestSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_subscription_with_active_subscription(self):
        self.send_command('/removesubscription 2015344951')
        add_response = self.send_command('/addsubscription 2015344951 30')
        add_expected_fragments = ["Subskrypcja dla użytkownika 2015344951 przedłużona do"]
        self.assert_response_contains(add_response, add_expected_fragments)

        subscription_response = self.send_command('/subskrypcja')
        subscription_expected_fragments = ["Pozostało dni: 30"]
        self.assert_response_contains(subscription_response, subscription_expected_fragments)

        self.send_command('/removesubscription 2015344951')

    @pytest.mark.quick
    def test_subscription_without_subscription(self):
        self.send_command('/removesubscription 2015344951')
        subscription_response = self.send_command('/subskrypcja')
        subscription_expected_fragments = ["🚫 Nie masz aktywnej subskrypcji.🚫"]
        self.assert_response_contains(subscription_response, subscription_expected_fragments)
