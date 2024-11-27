import pytest

from bot.tests.base_test import BaseTest


class TestAddKeyCommand(BaseTest):
    @pytest.mark.quick
    def test_add_key_valid(self):
        self.send_command('/removekey 30 tajny_klucz')
        self.expect_command_result_contains(
            '/addkey 30 tajny_klucz',
            ["✅ Stworzono klucz: `tajny_klucz` na 30 dni. ✅"]
        )
        self.expect_command_result_contains(
            '/removekey tajny_klucz',
            ["✅ Klucz `tajny_klucz` został usunięty. ✅"]
        )

    @pytest.mark.quick
    def test_add_key_zero_days(self):
        self.send_command('/removekey klucz_na_zero_dni')
        self.expect_command_result_contains(
            '/addkey 0 klucz_na_zero_dni',
            ["✅ Stworzono klucz: `klucz_na_zero_dni` na 0 dni. ✅"]
        )

    @pytest.mark.long
    def test_add_key_negative_days(self):
        self.send_command('/removekey klucz_na_ujemne_dni')
        self.expect_command_result_contains(
            '/addkey -30 klucz_na_ujemne_dni',
            ["✅ Stworzono klucz: `klucz_na_ujemne_dni` na -30 dni. ✅"]
        )

    @pytest.mark.long
    def test_add_key_invalid_days_format(self):
        self.expect_command_result_contains(
            '/addkey trzydzieści klucz_tekstowy_dni',
            ["⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"]
        )

    @pytest.mark.long
    def test_add_key_empty_note(self):
        self.expect_command_result_contains(
            '/addkey 30',
            ["❌ Podaj liczbę dni i klucz. Przykład: /addkey 30 tajny_klucz ❌"]
        )

    @pytest.mark.long
    def test_add_key_special_characters_in_note(self):
        self.expect_command_result_contains(
            '/addkey 30 specjalny@klucz#!',
            ["✅ Stworzono klucz: `specjalny@klucz#!` na 30 dni. ✅"]
        )
        self.expect_command_result_contains(
            '/removekey specjalny@klucz#!',
            ["✅ Klucz `specjalny@klucz#!` został usunięty. ✅"]
        )
