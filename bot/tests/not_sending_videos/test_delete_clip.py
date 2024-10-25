import pytest

from bot.tests.base_test import BaseTest


class TestDeleteClipCommand(BaseTest):

    @pytest.mark.quick
    def test_delete_existing_clip(self):
        self.send_command('/klip cytat')
        save_response = self.send_command('/zapisz test_clip')
        save_expected_fragments = ["✅ Klip 'test_clip' został zapisany pomyślnie. ✅"]
        self.assert_response_contains(save_response, save_expected_fragments)

        delete_response = self.send_command('/usunklip 1')
        delete_expected_fragments = ["Klip 'test_clip' został usunięty."]
        self.assert_response_contains(delete_response, delete_expected_fragments)

    @pytest.mark.quick
    def test_delete_nonexistent_clip(self):
        response = self.send_command('/usunklip 1337')
        expected_fragments = ["⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_delete_multiple_clips(self):
        self.send_command('/klip pierwszy')
        self.send_command('/zapisz pierwszy_clip')

        self.send_command('/klip drugi')
        self.send_command('/zapisz drugi_clip')

        delete_response_1 = self.send_command('/usunklip 1')
        delete_expected_fragments_1 = ["✅ Klip o nazwie 'pierwszy_clip' został usunięty.✅"]
        self.assert_response_contains(delete_response_1, delete_expected_fragments_1)

        delete_response_2 = self.send_command('/usunklip 1')
        delete_expected_fragments_2 = ["✅ Klip o nazwie 'drugi_clip' został usunięty.✅"]
        self.assert_response_contains(delete_response_2, delete_expected_fragments_2)

    @pytest.mark.long
    def test_delete_clip_with_special_characters(self):
        self.send_command('/klip cytat specjalny')
        save_response = self.send_command('/zapisz spec@l_clip!')
        save_expected_fragments = ["✅ Klip 'spec@l_clip!' został zapisany pomyślnie. ✅"]
        self.assert_response_contains(save_response, save_expected_fragments)

        delete_response = self.send_command('/usunklip 1')
        delete_expected_fragments = ["✅ Klip o nazwie 'spec@l_clip!' został usunięty.✅"]
        self.assert_response_contains(delete_response, delete_expected_fragments)
