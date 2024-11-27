import pytest

from bot.tests.base_test import BaseTest


class TestListWhitelistCommand(BaseTest):

    @pytest.mark.quick
    def test_list_whitelist_with_users(self):
        self.expect_command_result_contains('/listwhitelist', ["Lista użytkowników w Whitelist:"])
