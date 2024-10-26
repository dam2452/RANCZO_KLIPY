import pytest

from bot.tests.base_test import BaseTest


class TestClipSaveCommand(BaseTest):

    @pytest.mark.quick
    def test_save_clip_valid_name(self):
        self.send_command("/klip traktor")
        save_command = '/zapisz traktor'
        save_expected_fragments = ["✅ Klip 'traktor' został zapisany pomyślnie. ✅"]
        response_save = self.send_command(save_command)
        self.assert_response_contains(response_save, save_expected_fragments)

        list_command = '/mojeklipy'
        list_expected_fragments = ["traktor"]
        response_list = self.send_command(list_command)
        self.assert_response_contains(response_list, list_expected_fragments)

        self.send_command("/usunklip 1")

    @pytest.mark.quick
    def test_save_clip_without_name(self):
        save_command = '/zapisz'
        save_expected_fragments = ["📝 Podaj nazwę klipu. Przykład: /zapisz nazwa_klipu"]
        response_save = self.send_command(save_command)
        self.assert_response_contains(response_save, save_expected_fragments)

    @pytest.mark.long
    def test_save_clip_special_characters_in_name(self):
        self.send_command("/klip traktor")
        save_command = '/zapisz traktor@#!$'
        save_expected_fragments = ["✅ Klip 'traktor@#!$' został zapisany pomyślnie. ✅"]
        response_save = self.send_command(save_command)
        self.assert_response_contains(response_save, save_expected_fragments)

        list_command = '/mojeklipy'
        list_expected_fragments = ["traktor@#!$"]
        response_list = self.send_command(list_command)
        self.assert_response_contains(response_list, list_expected_fragments)

        self.send_command("/usunklip 1")

    @pytest.mark.long
    def test_save_clip_duplicate_name(self):
        self.send_command("/klip traktor")
        save_command = '/zapisz traktor'
        save_expected_fragments = ["✅ Klip 'traktor' został zapisany pomyślnie. ✅"]
        response_save = self.send_command(save_command)
        self.assert_response_contains(response_save, save_expected_fragments)

        response_duplicate_save = self.send_command(save_command)
        duplicate_save_expected_fragments = ["⚠️ Klip o takiej nazwie 'traktor' już istnieje. Wybierz inną nazwę.⚠️"]
        self.assert_response_contains(response_duplicate_save, duplicate_save_expected_fragments)

        self.send_command("/usunklip 1")
