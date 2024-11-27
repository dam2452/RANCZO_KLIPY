import pytest

from bot.tests.base_test import BaseTest


class TestMyClipsCommand(BaseTest):
    @pytest.mark.quick
    def test_myclips_no_clips(self):
        self.expect_command_result_contains('/mojeklipy', ["📭 Nie masz zapisanych klipów.📭"])

    @pytest.mark.long
    def test_myclips_with_clips(self):
        self.send_command('/klip cytat')
        self.expect_command_result_contains('/zapisz test_clip', ["✅ Klip 'test_clip' został zapisany pomyślnie. ✅"])
        self.expect_command_result_contains('/mojeklipy', ["test_clip"])
        self.expect_command_result_contains('/usunklip 1', ["✅ Klip o nazwie 'test_clip' został usunięty.✅"])
