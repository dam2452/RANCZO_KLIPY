import pytest

from bot.tests.base_test import BaseTest


class TestRemoveKeyCommand(BaseTest):

    @pytest.mark.quick
    def test_remove_existing_key(self):
        add_response = self.send_command('/addkey 30 tajny_klucz')
        add_expected_fragments = ["✅ Stworzono klucz: `tajny_klucz` na 30 dni. ✅"]
        self.assert_response_contains(add_response, add_expected_fragments)

        remove_response = self.send_command('/removekey tajny_klucz')
        remove_expected_fragments = ["✅ Klucz `tajny_klucz` został usunięty. ✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)

    @pytest.mark.quick
    def test_remove_nonexistent_key(self):
        remove_response = self.send_command('/removekey nieistniejacy_klucz')
        remove_expected_fragments = ["❌ Nie znaleziono klucza `nieistniejacy_klucz`. ❌"]
        self.assert_response_contains(remove_response, remove_expected_fragments)

    @pytest.mark.long
    def test_remove_key_with_special_characters(self):
        add_response = self.send_command('/addkey 30 specjalny@klucz#!')
        add_expected_fragments = ["✅ Stworzono klucz: `specjalny@klucz#!` na 30 dni. ✅"]
        self.assert_response_contains(add_response, add_expected_fragments)

        remove_response = self.send_command('/removekey specjalny@klucz#!')
        remove_expected_fragments = ["✅ Klucz `specjalny@klucz#!` został usunięty. ✅"]
        self.assert_response_contains(remove_response, remove_expected_fragments)

    @pytest.mark.long
    def test_remove_key_twice(self):
        add_response = self.send_command('/addkey 30 klucz_do_usuniecia')
        add_expected_fragments = ["✅ Stworzono klucz: `klucz_do_usuniecia` na 30 dni. ✅"]
        self.assert_response_contains(add_response, add_expected_fragments)

        first_remove_response = self.send_command('/removekey klucz_do_usuniecia')
        first_remove_expected_fragments = ["✅ Klucz `klucz_do_usuniecia` został usunięty. ✅"]
        self.assert_response_contains(first_remove_response, first_remove_expected_fragments)

        second_remove_response = self.send_command('/removekey klucz_do_usuniecia')
        second_remove_expected_fragments = ["❌ Nie znaleziono klucza `klucz_do_usuniecia`. ❌"]
        self.assert_response_contains(second_remove_response, second_remove_expected_fragments)
