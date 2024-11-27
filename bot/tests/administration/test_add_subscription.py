import pytest

from bot.tests.base_test import BaseTest


class TestAddSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_add_subscription_valid_user(self):
        self.expect_command_result_contains(
            '/addsub 2015344951 30',
            ["✅ Subskrypcja dla użytkownika 2015344951"]
        )

    @pytest.mark.quick
    def test_add_subscription_nonexistent_user(self):
        self.expect_command_result_contains(
            '/addsubscription 999999999 30',
            ["⚠️ Wystąpił błąd podczas przedłużania subskrypcji.⚠️"]
        )

    @pytest.mark.long
    def test_add_subscription_invalid_days_format(self):
        self.expect_command_result_contains(
            '/addsubscription 123456789 trzydzieści',
            ["⚠️ Nie podano ID użytkownika ani ilości dni.⚠️"]
        )

    @pytest.mark.long
    def test_add_subscription_invalid_user_id_format(self):
        self.expect_command_result_contains(
            '/addsubscription user123 30',
            ["⚠️ Nie podano ID użytkownika ani ilości dni.⚠️"]
        )

    @pytest.mark.long
    def test_add_subscription_negative_days(self):
        self.expect_command_result_contains(
            '/addsubscription 123456789 -30',
            ["⚠️ Nie podano ID użytkownika ani ilości dni.⚠️"]
        )
