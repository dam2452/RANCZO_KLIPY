import pytest

from bot.tests.base_test import BaseTest


class TestClipSaveCommand(BaseTest):

    @pytest.mark.quick
    def test_save_clip(self):
        save_command = '/zapisz traktor'
        save_expected_fragments = ["Klip został zapisany jako 'traktor'."]
        response_save = self.send_command(save_command)
        self.assert_response_contains(response_save, save_expected_fragments)

        list_command = '/mojeklipy'
        list_expected_fragments = ["traktor"]
        response_list = self.send_command(list_command)
        self.assert_response_contains(response_list, list_expected_fragments)
