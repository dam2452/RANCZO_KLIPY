import pytest

from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestAdminCommand(BaseTest):
    pass
    # @pytest.mark.quick
    # @pytest.mark.asyncio
    # async def test_admin_help(self):
    #     await self.expect_command_result_contains(
    #         '/admin',
    #         [msg.get_admin_help_message()],
    #     )
    #
    # @pytest.mark.quick
    # @pytest.mark.asyncio
    # async def test_admin_shortcuts(self):
    #     await self.expect_command_result_contains(
    #         '/admin skroty',
    #         [msg.get_admin_shortcuts_message()],
    #     )
    #
    # @pytest.mark.asyncio
    # async def test_admin_invalid_command(self):
    #     await self.expect_command_result_contains(
    #         '/admin nieistniejace_polecenie',
    #         [msg.get_admin_help_message()],
    #     )
