import pytest

from bot.tests.base_test import BaseTest


class TestUseKeyCommand(BaseTest):

    @pytest.mark.quick
    def test_use_existing_key(self):
        self.send_command('/removekey aktywny_klucz')
        add_response = self.send_command('/addkey 30 aktywny_klucz')
        add_expected_fragments = ["✅ Stworzono klucz: `aktywny_klucz` na 30 dni. ✅"]
        self.assert_response_contains(add_response, add_expected_fragments)

        use_key_response = self.send_command('/klucz aktywny_klucz')
        use_key_expected_fragments = ["🎉 Subskrypcja przedłużona o 30 dni! 🎉"]
        self.assert_response_contains(use_key_response, use_key_expected_fragments)

        self.send_command('/removekey aktywny_klucz')

    @pytest.mark.quick
    def test_use_nonexistent_key(self):
        use_key_response = self.send_command('/klucz nieistniejacy_klucz')
        use_key_expected_fragments = ["❌ Podany klucz jest niepoprawny lub został już wykorzystany. ❌"]
        self.assert_response_contains(use_key_response, use_key_expected_fragments)

    @pytest.mark.long
    def test_use_key_with_special_characters(self):
        self.send_command('/removekey spec@l_key!')
        add_response = self.send_command('/addkey 30 spec@l_key!')
        add_expected_fragments = ["✅ Stworzono klucz: `spec@l_key!` na 30 dni. ✅"]
        self.assert_response_contains(add_response, add_expected_fragments)

        use_key_response = self.send_command('/klucz spec@l_key!')
        use_key_expected_fragments = ["🎉 Subskrypcja przedłużona o 30 dni! 🎉"]
        self.assert_response_contains(use_key_response, use_key_expected_fragments)

        self.send_command('/removekey spec@l_key!')

    @pytest.mark.long
    def test_use_key_twice(self):
        self.send_command('/removekey klucz_jednorazowy')
        add_response = self.send_command('/addkey 30 klucz_jednorazowy')
        add_expected_fragments = ["✅ Stworzono klucz: `klucz_jednorazowy` na 30 dni. ✅"]
        self.assert_response_contains(add_response, add_expected_fragments)

        first_use_response = self.send_command('/klucz klucz_jednorazowy')
        first_use_expected_fragments = ["🎉 Subskrypcja przedłużona o 30 dni! 🎉"]
        self.assert_response_contains(first_use_response, first_use_expected_fragments)

        second_use_response = self.send_command('/klucz klucz_jednorazowy')
        second_use_expected_fragments = ["❌ Podany klucz jest niepoprawny lub został już wykorzystany. ❌"]
        self.assert_response_contains(second_use_response, second_use_expected_fragments)

        self.send_command('/removekey klucz_jednorazowy')

    @pytest.mark.long
    def test_use_key_without_content(self):
        use_key_response = self.send_command('/klucz')
        use_key_expected_fragments = ["⚠️ Nie podano klucza.⚠️ Przykład: /klucz tajny_klucz"]
        self.assert_response_contains(use_key_response, use_key_expected_fragments)
