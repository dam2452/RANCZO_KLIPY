import pytest

from bot.tests.base_test import BaseTest


class TestAddKeyCommand(BaseTest):
    # pylint: disable=duplicate-code
    @pytest.mark.quick
    def test_add_key_valid(self):
        self.send_command('/removekey 30 tajny_klucz')
        add_response = self.send_command('/addkey 30 tajny_klucz')
        add_expected_fragments = ["✅ Stworzono klucz: `tajny_klucz` na 30 dni. ✅"]
        self.assert_response_contains(add_response, add_expected_fragments)

        remove_response = self.send_command('/removekey tajny_klucz')
        remove_expected_fragments = ["✅ Klucz `tajny_klucz` został usunięty. ✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)
    #pylint: enable=duplicate-code
    @pytest.mark.quick
    def test_add_key_zero_days(self):
        self.send_command('/removekey klucz_na_zero_dni')
        add_response = self.send_command('/addkey 0 klucz_na_zero_dni')
        add_expected_fragments = ["✅ Stworzono klucz: `klucz_na_zero_dni` na 0 dni. ✅"]
        self.assert_response_contains(add_response, add_expected_fragments)

    @pytest.mark.long
    def test_add_key_negative_days(self):
        self.send_command('/removekey klucz_na_ujemne_dni')
        add_response = self.send_command('/addkey -30 klucz_na_ujemne_dni')
        add_expected_fragments = ["✅ Stworzono klucz: `klucz_na_ujemne_dni` na -30 dni. ✅"]
        self.assert_response_contains(add_response, add_expected_fragments)

    @pytest.mark.long
    def test_add_key_invalid_days_format(self):
        add_response = self.send_command('/addkey trzydzieści klucz_tekstowy_dni')
        add_expected_fragments = ["⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"]
        self.assert_response_contains(add_response, add_expected_fragments)

    @pytest.mark.long
    def test_add_key_empty_note(self):
        add_response = self.send_command('/addkey 30')
        add_expected_fragments = ["❌ Podaj liczbę dni i klucz. Przykład: /addkey 30 tajny_klucz ❌"]
        self.assert_response_contains(add_response, add_expected_fragments)

    # pylint: disable=duplicate-code
    @pytest.mark.long
    def test_add_key_special_characters_in_note(self):
        add_response = self.send_command('/addkey 30 specjalny@klucz#!')
        add_expected_fragments = ["✅ Stworzono klucz: `specjalny@klucz#!` na 30 dni. ✅"]
        self.assert_response_contains(add_response, add_expected_fragments)

        remove_response = self.send_command('/removekey specjalny@klucz#!')
        remove_expected_fragments = ["✅ Klucz `specjalny@klucz#!` został usunięty. ✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)
    #pylint: enable=duplicate-code
