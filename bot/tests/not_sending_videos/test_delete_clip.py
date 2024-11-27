import pytest
from bot.tests.base_test import BaseTest


class TestDeleteClipCommand(BaseTest):

    @pytest.mark.quick
    def test_delete_existing_clip(self):
        self.send_command('/klip cytat')
        self.expect_command_result_contains('/zapisz test_clip', ["✅ Klip 'test_clip' został zapisany pomyślnie. ✅"])
        self.expect_command_result_contains('/usunklip 1', ["✅ Klip o nazwie 'test_clip' został usunięty.✅"])

    @pytest.mark.quick
    def test_delete_nonexistent_clip(self):
        self.expect_command_result_contains(
            '/usunklip 1337',
            ["⚠️ Wystąpił błąd podczas przetwarzania żądania. Prosimy spróbować ponownie później.⚠️"]
        )

    @pytest.mark.long
    def test_delete_multiple_clips(self):
        self.send_command('/klip pierwszy')
        self.expect_command_result_contains('/zapisz pierwszy_clip', ["✅ Klip 'pierwszy_clip' został zapisany pomyślnie. ✅"])

        self.send_command('/klip drugi')
        self.expect_command_result_contains('/zapisz drugi_clip', ["✅ Klip 'drugi_clip' został zapisany pomyślnie. ✅"])

        self.expect_command_result_contains('/usunklip 1', ["✅ Klip o nazwie 'pierwszy_clip' został usunięty.✅"])
        self.expect_command_result_contains('/usunklip 1', ["✅ Klip o nazwie 'drugi_clip' został usunięty.✅"])

    @pytest.mark.long
    def test_delete_clip_with_special_characters(self):
        self.send_command('/klip cytat specjalny')
        self.expect_command_result_contains('/zapisz spec@l_clip!', ["✅ Klip 'spec@l_clip!' został zapisany pomyślnie. ✅"])
        self.expect_command_result_contains('/usunklip 1', ["✅ Klip o nazwie 'spec@l_clip!' został usunięty.✅"])
