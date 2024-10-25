import pytest

from bot.tests.base_test import BaseTest


class TestRemoveWhitelistCommand(BaseTest):

    @pytest.mark.quick
    def test_remove_existing_user_whitelist(self):
        add_response = self.send_command('/addwhitelist 6967485026')
        add_expected_fragments = ["Dodano","do whitelisty."]
        self.assert_response_contains(add_response, add_expected_fragments)

        remove_response = self.send_command('/removewhitelist 6967485026')
        remove_expected_fragments = ["✅ Użytkownik o ID 6967485026 został usunięty z whitelisty. ✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)

    @pytest.mark.quick
    def test_remove_nonexistent_user_whitelist(self):
        remove_response = self.send_command('/removewhitelist 6967485026')
        remove_expected_fragments = ["✅ Usunięto 6967485026 z whitelisty.✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)

    @pytest.mark.long
    def test_remove_user_whitelist_twice(self):
        add_response = self.send_command('/addwhitelist 123456789')
        add_expected_fragments = ["Użytkownik o ID 123456789 został dodany do whitelisty."]
        self.assert_response_contains(add_response, add_expected_fragments)

        first_remove_response = self.send_command('/removewhitelist 123456789')
        first_remove_expected_fragments = ["✅ Użytkownik o ID 123456789 został usunięty z whitelisty. ✅"]
        self.assert_response_contains(first_remove_response, first_remove_expected_fragments)

        second_remove_response = self.send_command('/removewhitelist 123456789')
        second_remove_expected_fragments = ["❌ Użytkownik o ID 123456789 nie znajduje się na whitelistie. ❌"]
        self.assert_response_contains(second_remove_response, second_remove_expected_fragments)

    @pytest.mark.long
    def test_remove_whitelist_invalid_user_id_format(self):
        remove_response = self.send_command('/removewhitelist user123')
        expected_fragments = ["⚠️ Nie podano ID użytkownika.⚠️"]
        self.assert_response_contains(remove_response, expected_fragments)
