import pytest

from bot.tests.base_test import BaseTest


class TestListAdminsCommand(BaseTest):

    @pytest.mark.quick
    def test_list_admins_with_admins(self):
        response = self.send_command('/listadmins')
        expected_fragments = ["2015344951"]
        self.assert_response_contains(response, expected_fragments)
