import pytest

from bot.tests.base_test import BaseTest


class TestNoteCommand(BaseTest):

    @pytest.mark.quick
    def test_add_note_with_valid_user_and_content(self):
        self.expect_command_result_contains(
            '/note 2015344951 notatka123',
            ["✅ Notatka została zaktualizowana.✅"]
        )

    @pytest.mark.quick
    def test_note_missing_user_id_and_content(self):
        self.expect_command_result_contains(
            '/note',
            ["❌ Proszę podać ID użytkownika oraz treść notatki.❌"]
        )

    @pytest.mark.quick
    def test_note_missing_content(self):
        self.expect_command_result_contains(
            '/note 2015344951',
            ["❌ Proszę podać ID użytkownika oraz treść notatki.❌"]
        )

    @pytest.mark.long
    def test_note_with_special_characters_in_content(self):
        self.expect_command_result_contains(
            '/note 2015344951 notatka@#!$%&*()',
            ["✅ Notatka została zaktualizowana.✅"]
        )

    @pytest.mark.long
    def test_note_with_invalid_user_id_format(self):
        self.expect_command_result_contains(
            '/note user123 notatka_testowa',
            ["❌ Nieprawidłowe ID użytkownika: user123.❌"]
        )

    @pytest.mark.long
    def test_note_with_long_content(self):
        long_content = "to jest bardzo długa notatka " * 10
        self.expect_command_result_contains(
            f'/note 2015344951 {long_content}',
            ["✅ Notatka została zaktualizowana.✅"]
        )
