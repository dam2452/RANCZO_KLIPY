import pytest

from bot.tests.base_test import BaseTest


class TestRemoveWhitelistCommand(BaseTest):

    @pytest.mark.quick
    def test_remove_existing_user_whitelist(self):
        self.expect_command_result_contains(
            '/addwhitelist 6967485026',
            ["Dodano", "do whitelisty."]
        )
        self.expect_command_result_contains(
            '/removewhitelist 6967485026',
            ["✅ Użytkownik o ID 6967485026 został usunięty z whitelisty. ✅"]
        )

    @pytest.mark.quick
    def test_remove_nonexistent_user_whitelist(self):
        self.expect_command_result_contains(
            '/removewhitelist 6967485026',
            ["✅ Usunięto 6967485026 z whitelisty.✅"]
        )

    @pytest.mark.long
    def test_remove_user_whitelist_twice(self):
        self.expect_command_result_contains(
            '/addwhitelist 123456789',
            ["Użytkownik o ID 123456789 został dodany do whitelisty."]
        )
        self.expect_command_result_contains(
            '/removewhitelist 123456789',
            ["✅ Użytkownik o ID 123456789 został usunięty z whitelisty. ✅"]
        )
        self.expect_command_result_contains(
            '/removewhitelist 123456789',
            ["❌ Użytkownik o ID 123456789 nie znajduje się na whitelistie. ❌"]
        )

    @pytest.mark.long
    def test_remove_whitelist_invalid_user_id_format(self):
        self.expect_command_result_contains(
            '/removewhitelist user123',
            ["⚠️ Nie podano ID użytkownika.⚠️"]
        )
