import pytest

from bot.tests.base_test import BaseTest


class TestRemoveSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_remove_existing_subscription(self):
        self.expect_command_result_contains(
            '/addsubscription 2015344951 30',
            ["Subskrypcja dla użytkownika 2015344951"]
        )
        self.expect_command_result_contains(
            '/removesubscription 2015344951',
            ["✅ Subskrypcja dla użytkownika 2015344951 została usunięta.✅"]
        )

    @pytest.mark.quick
    def test_remove_nonexistent_subscription(self):
        self.expect_command_result_contains(
            '/removesubscription 987654321',
            ["✅ Subskrypcja dla użytkownika 987654321 została usunięta.✅"]
        )

    @pytest.mark.long
    def test_remove_subscription_twice(self):
        self.expect_command_result_contains(
            '/addsubscription 2015344951 30',
            ["Subskrypcja dla użytkownika 2015344951"]
        )
        self.expect_command_result_contains(
            '/removesubscription 2015344951',
            ["✅ Subskrypcja dla użytkownika 2015344951 została usunięta.✅"]
        )
        self.expect_command_result_contains(
            '/removesubscription 2015344951',
            ["✅ Subskrypcja dla użytkownika 2015344951 została usunięta.✅"]
        )

    @pytest.mark.long
    def test_remove_subscription_invalid_user_id_format(self):
        self.expect_command_result_contains(
            '/removesubscription user123',
            ["✅ Subskrypcja dla użytkownika user123 została usunięta.✅"]
        )
