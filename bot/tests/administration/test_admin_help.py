import pytest

import bot.responses.administration.admin_help_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestAdminCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_admin_help(self):
        await self.expect_command_result_contains(
            '/admin',
            [self.remove_first_line(msg.get_admin_help_message())],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_admin_shortcuts(self):
        await self.expect_command_result_contains(
            '/admin skroty',
            [self.remove_first_line(msg.get_admin_shortcuts_message())],
        )

    @pytest.mark.asyncio
    async def test_admin_invalid_command(self):
        await self.expect_command_result_contains(
            '/admin nieistniejace_polecenie',
            [self.remove_first_line(msg.get_admin_help_message())],
        )
