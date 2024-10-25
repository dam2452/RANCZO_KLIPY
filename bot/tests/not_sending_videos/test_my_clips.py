import pytest

from bot.tests.base_test import BaseTest


class TestMyClipsCommand(BaseTest):
    @pytest.mark.quick
    def test_myclips_no_clips(self):
        response = self.send_command('/mojeklipy')
        expected_fragments = ["📭 Nie masz zapisanych klipów.📭"]
        self.assert_response_contains(response, expected_fragments)

    @pytest.mark.long
    def test_myclips_with_clips(self):
        self.send_command('/klip cytat')
        save_response = self.send_command('/zapisz test_clip')
        save_expected_fragments = ["✅ Klip 'test_clip' został zapisany pomyślnie. ✅"]
        self.assert_response_contains(save_response, save_expected_fragments)

        response = self.send_command('/mojeklipy')
        expected_fragments = ["test_clip"]
        self.assert_response_contains(response, expected_fragments)

        delete_response = self.send_command('/usunklip 1')
        delete_expected_fragments = ["✅ Klip o nazwie 'test_clip' został usunięty.✅"]
        self.assert_response_contains(delete_response, delete_expected_fragments)