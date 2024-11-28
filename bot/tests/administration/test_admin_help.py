import pytest

import bot.responses.administration.admin_help_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestAdminCommand(BaseTest):

    @pytest.mark.quick
    def test_admin_base_command(self):
        self.expect_command_result_contains(
            '/admin',
            [msg.get_admin_help_message()],
        )

    @pytest.mark.long
    def test_admin_shortcuts(self):
        self.expect_command_result_contains(
            '/admin skroty',
            [msg.get_admin_shortcuts_message()],
        )

    @pytest.mark.long
    def test_admin_invalid_command(self):
        self.expect_command_result_contains(
            '/admin nieistniejace_polecenie',
            [msg.get_admin_help_message()],
        )
