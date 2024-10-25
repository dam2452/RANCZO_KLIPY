import pytest

from bot.tests.base_test import BaseTest


class TestWhitelistCommands(BaseTest):

    @pytest.mark.quick
    def test_add_and_remove_valid_user_whitelist(self):
        add_response = self.send_command('/addwhitelist 123456789')
        add_expected_fragments = ["Użytkownik o ID 123456789 został dodany do whitelisty."]
        self.assert_response_contains(add_response, add_expected_fragments)

        remove_response = self.send_command('/removewhitelist 123456789')
        remove_expected_fragments = ["✅ Usunięto 123456789 z whitelisty.✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)

    @pytest.mark.quick
    def test_add_nonexistent_user_whitelist(self):
        add_response = self.send_command('/addwhitelist 999999999')
        add_expected_fragments = ["Użytkownik o ID 999999999 został dodany do whitelisty."]
        self.assert_response_contains(add_response, add_expected_fragments)

        remove_response = self.send_command('/removewhitelist 999999999')
        remove_expected_fragments = ["✅ Usunięto 999999999 z whitelisty.✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)

    @pytest.mark.long
    def test_add_whitelist_invalid_user_id_format(self):
        add_response = self.send_command('/addwhitelist user123')
        add_expected_fragments = ["❌ Niepoprawny format ID użytkownika. Użyj liczby całkowitej."]
        self.assert_response_contains(add_response, add_expected_fragments)

    @pytest.mark.long
    def test_remove_nonexistent_user_whitelist(self):
        remove_response = self.send_command('/removewhitelist 888888888')
        remove_expected_fragments = ["✅ Usunięto 888888888 z whitelisty.✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)
