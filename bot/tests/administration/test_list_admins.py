import pytest

from bot.tests.base_test import BaseTest


class TestListAdminsCommand(BaseTest):

    @pytest.mark.quick
    def test_list_admins_with_admins(self):
        self.expect_command_result_contains('/listadmins', ["2015344951"])
