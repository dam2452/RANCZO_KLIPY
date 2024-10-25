import pytest

from bot.tests.base_test import BaseTest


class TestNoteCommand(BaseTest):

    @pytest.mark.quick
    def test_add_note_with_valid_user_and_content(self):
        note_response = self.send_command('/note 2015344951 notatka123')
        expected_fragments = ["✅ Notatka została zaktualizowana.✅"]
        self.assert_response_contains(note_response, expected_fragments)

    @pytest.mark.quick
    def test_note_missing_user_id_and_content(self):
        note_response = self.send_command('/note')
        expected_fragments = ["❌ Proszę podać ID użytkownika oraz treść notatki.❌"]
        self.assert_response_contains(note_response, expected_fragments)

    @pytest.mark.quick
    def test_note_missing_content(self):
        note_response = self.send_command('/note 2015344951')
        expected_fragments = ["❌ Proszę podać ID użytkownika oraz treść notatki.❌"]
        self.assert_response_contains(note_response, expected_fragments)

    @pytest.mark.long
    def test_note_with_special_characters_in_content(self):
        note_response = self.send_command('/note 2015344951 notatka@#!$%&*()')
        expected_fragments = ["✅ Notatka została zaktualizowana.✅"]
        self.assert_response_contains(note_response, expected_fragments)

    @pytest.mark.long
    def test_note_with_invalid_user_id_format(self):
        note_response = self.send_command('/note user123 notatka_testowa')
        expected_fragments = ["❌ Nieprawidłowe ID użytkownika: user123.❌"]
        self.assert_response_contains(note_response, expected_fragments)

    @pytest.mark.long
    def test_note_with_long_content(self):
        long_content = "to jest bardzo długa notatka " * 10
        note_response = self.send_command(f'/note 2015344951 {long_content}')
        expected_fragments = ["✅ Notatka została zaktualizowana.✅"]
        self.assert_response_contains(note_response, expected_fragments)
