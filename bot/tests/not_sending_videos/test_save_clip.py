import pytest

from bot.tests.base_test import BaseTest


class TestClipSaveCommand(BaseTest):

    @pytest.mark.quick
    def test_save_clip_valid_name(self):
        self.send_command("/klip traktor")
        self.expect_command_result_contains('/zapisz traktor', ["✅ Klip 'traktor' został zapisany pomyślnie. ✅"])
        self.expect_command_result_contains('/mojeklipy', ["traktor"])
        self.send_command("/usunklip 1")

    @pytest.mark.quick
    def test_save_clip_without_name(self):
        self.expect_command_result_contains(
            '/zapisz', ["📝 Podaj nazwę klipu. Przykład: /zapisz nazwa_klipu"]
        )

    @pytest.mark.long
    def test_save_clip_special_characters_in_name(self):
        self.send_command("/klip traktor")
        self.expect_command_result_contains('/zapisz traktor@#!$', ["✅ Klip 'traktor@#!$' został zapisany pomyślnie. ✅"])
        self.expect_command_result_contains('/mojeklipy', ["traktor@#!$"])
        self.send_command("/usunklip 1")

    @pytest.mark.long
    def test_save_clip_duplicate_name(self):
        self.send_command("/klip traktor")
        self.expect_command_result_contains('/zapisz traktor', ["✅ Klip 'traktor' został zapisany pomyślnie. ✅"])
        self.expect_command_result_contains(
            '/zapisz traktor', ["⚠️ Klip o takiej nazwie 'traktor' już istnieje. Wybierz inną nazwę.⚠️"]
        )
        self.send_command("/usunklip 1")
