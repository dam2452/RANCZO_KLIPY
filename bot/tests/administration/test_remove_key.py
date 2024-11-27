import pytest

from bot.tests.base_test import BaseTest


class TestRemoveKeyCommand(BaseTest):

    @pytest.mark.quick
    def test_remove_existing_key(self):
        self.expect_command_result_contains(
            '/addkey 30 tajny_klucz',
            ["✅ Stworzono klucz: `tajny_klucz` na 30 dni. ✅"]
        )
        self.expect_command_result_contains(
            '/removekey tajny_klucz',
            ["✅ Klucz `tajny_klucz` został usunięty. ✅"]
        )

    @pytest.mark.quick
    def test_remove_nonexistent_key(self):
        self.expect_command_result_contains(
            '/removekey nieistniejacy_klucz',
            ["❌ Nie znaleziono klucza `nieistniejacy_klucz`. ❌"]
        )

    @pytest.mark.long
    def test_remove_key_with_special_characters(self):
        self.expect_command_result_contains(
            '/addkey 30 specjalny@klucz#!',
            ["✅ Stworzono klucz: `specjalny@klucz#!` na 30 dni. ✅"]
        )
        self.expect_command_result_contains(
            '/removekey specjalny@klucz#!',
            ["✅ Klucz `specjalny@klucz#!` został usunięty. ✅"]
        )

    @pytest.mark.long
    def test_remove_key_twice(self):
        self.expect_command_result_contains(
            '/addkey 30 klucz_do_usuniecia',
            ["✅ Stworzono klucz: `klucz_do_usuniecia` na 30 dni. ✅"]
        )
        self.expect_command_result_contains(
            '/removekey klucz_do_usuniecia',
            ["✅ Klucz `klucz_do_usuniecia` został usunięty. ✅"]
        )
        self.expect_command_result_contains(
            '/removekey klucz_do_usuniecia',
            ["❌ Nie znaleziono klucza `klucz_do_usuniecia`. ❌"]
        )
