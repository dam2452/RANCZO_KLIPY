import pytest

from bot.tests.base_test import BaseTest


class TestAddSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_add_subscription_valid_user(self):
        response = self.send_command('/addsub 2015344951 30')
        expected_fragments = ["✅ Subskrypcja dla użytkownika 2015344951 przedłużona do 2024-11-24.✅"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.quick
    def test_add_subscription_nonexistent_user(self):
        response = self.send_command('/addsubscription 999999999 30')
        expected_fragments = ["⚠️ Wystąpił błąd podczas przedłużania subskrypcji.⚠️"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_add_subscription_invalid_days_format(self):
        response = self.send_command('/addsubscription 123456789 trzydzieści')
        expected_fragments = ["⚠️ Nie podano ID użytkownika ani ilości dni.⚠️"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_add_subscription_invalid_user_id_format(self):
        response = self.send_command('/addsubscription user123 30')
        expected_fragments = ["⚠️ Nie podano ID użytkownika ani ilości dni.⚠️"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_add_subscription_negative_days(self):
        response = self.send_command('/addsubscription 123456789 -30')
        expected_fragments = ["⚠️ Nie podano ID użytkownika ani ilości dni.⚠️"]
        self.assert_response_contains(response, expected_fragments)
