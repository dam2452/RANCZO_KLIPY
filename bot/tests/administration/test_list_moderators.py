import pytest

from bot.tests.base_test import BaseTest


class TestListModeratorsCommand(BaseTest):

    @pytest.mark.quick
    def test_list_moderators_with_moderators(self):
        self.expect_command_result_contains('/listmoderators', ["Lista moderatorów:"])
