import pytest

from bot.tests.base_test import BaseTest


class TestWhitelistCommands(BaseTest):

    @pytest.mark.quick
    def test_add_and_remove_valid_user_whitelist(self):
        self.expect_command_result_contains(
            '/addwhitelist 123456789',
            ["Użytkownik o ID 123456789 został dodany do whitelisty."]
        )
        self.expect_command_result_contains(
            '/removewhitelist 123456789',
            ["✅ Usunięto 123456789 z whitelisty.✅"]
        )

    @pytest.mark.quick
    def test_add_nonexistent_user_whitelist(self):
        self.expect_command_result_contains(
            '/addwhitelist 999999999',
            ["Użytkownik o ID 999999999 został dodany do whitelisty."]
        )
        self.expect_command_result_contains(
            '/removewhitelist 999999999',
            ["✅ Usunięto 999999999 z whitelisty.✅"]
        )

    @pytest.mark.long
    def test_add_whitelist_invalid_user_id_format(self):
        self.expect_command_result_contains(
            '/addwhitelist user123',
            ["❌ Niepoprawny format ID użytkownika. Użyj liczby całkowitej."]
        )

    @pytest.mark.long
    def test_remove_nonexistent_user_whitelist(self):
        self.expect_command_result_contains(
            '/removewhitelist 888888888',
            ["✅ Usunięto 888888888 z whitelisty.✅"]
        )
