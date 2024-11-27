import pytest

from bot.tests.base_test import BaseTest


class TestUseKeyCommand(BaseTest):

    @pytest.mark.quick
    def test_use_existing_key(self):
        self.send_command('/removekey aktywny_klucz')
        self.expect_command_result_contains(
            '/addkey 30 aktywny_klucz',
            ["✅ Stworzono klucz: `aktywny_klucz` na 30 dni. ✅"]
        )
        self.expect_command_result_contains(
            '/klucz aktywny_klucz',
            ["🎉 Subskrypcja przedłużona o 30 dni! 🎉"]
        )
        self.send_command('/removekey aktywny_klucz')

    @pytest.mark.quick
    def test_use_nonexistent_key(self):
        self.expect_command_result_contains(
            '/klucz nieistniejacy_klucz',
            ["❌ Podany klucz jest niepoprawny lub został już wykorzystany. ❌"]
        )

    @pytest.mark.long
    def test_use_key_with_special_characters(self):
        self.send_command('/removekey spec@l_key!')
        self.expect_command_result_contains(
            '/addkey 30 spec@l_key!',
            ["✅ Stworzono klucz: `spec@l_key!` na 30 dni. ✅"]
        )
        self.expect_command_result_contains(
            '/klucz spec@l_key!',
            ["🎉 Subskrypcja przedłużona o 30 dni! 🎉"]
        )
        self.send_command('/removekey spec@l_key!')

    @pytest.mark.long
    def test_use_key_twice(self):
        self.send_command('/removekey klucz_jednorazowy')
        self.expect_command_result_contains(
            '/addkey 30 klucz_jednorazowy',
            ["✅ Stworzono klucz: `klucz_jednorazowy` na 30 dni. ✅"]
        )
        self.expect_command_result_contains(
            '/klucz klucz_jednorazowy',
            ["🎉 Subskrypcja przedłużona o 30 dni! 🎉"]
        )
        self.expect_command_result_contains(
            '/klucz klucz_jednorazowy',
            ["❌ Podany klucz jest niepoprawny lub został już wykorzystany. ❌"]
        )
        self.send_command('/removekey klucz_jednorazowy')

    @pytest.mark.long
    def test_use_key_without_content(self):
        self.expect_command_result_contains(
            '/klucz',
            ["⚠️ Nie podano klucza.⚠️ Przykład: /klucz tajny_klucz"]
        )
