import pytest

from bot.tests.base_test import BaseTest


class TestRemoveSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    def test_remove_existing_subscription(self):
        add_response = self.send_command('/addsubscription 2015344951 30')
        add_expected_fragments = ["Subskrypcja dla użytkownika 2015344951"]
        self.assert_response_contains(add_response, add_expected_fragments)

        remove_response = self.send_command('/removesubscription 2015344951')
        remove_expected_fragments = ["✅ Subskrypcja dla użytkownika 2015344951 została usunięta.✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)

    @pytest.mark.quick
    def test_remove_nonexistent_subscription(self):
        remove_response = self.send_command('/removesubscription 987654321')
        remove_expected_fragments = ["✅ Subskrypcja dla użytkownika 987654321 została usunięta.✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)

    @pytest.mark.long
    def test_remove_subscription_twice(self):
        add_response = self.send_command('/addsubscription 2015344951 30')
        add_expected_fragments = ["Subskrypcja dla użytkownika 2015344951"]
        self.assert_response_contains(add_response, add_expected_fragments)

        first_remove_response = self.send_command('/removesubscription 2015344951')
        first_remove_expected_fragments = ["✅ Subskrypcja dla użytkownika 2015344951 została usunięta.✅"]
        self.assert_response_contains(first_remove_response, first_remove_expected_fragments)

        second_remove_response = self.send_command('/removesubscription 2015344951')
        second_remove_expected_fragments = ["✅ Subskrypcja dla użytkownika 2015344951 została usunięta.✅"]
        self.assert_response_contains(second_remove_response, second_remove_expected_fragments)

    @pytest.mark.long
    def test_remove_subscription_invalid_user_id_format(self):
        remove_response = self.send_command('/removesubscription user123')
        expected_fragments = ["✅ Subskrypcja dla użytkownika user123 została usunięta.✅"]
        self.assert_response_contains(remove_response, expected_fragments)
