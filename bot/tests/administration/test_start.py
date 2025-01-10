import pytest

from bot.database.response_keys import ResponseKey as RK
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestStartHandler(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_start_base_command(self):
        await self.expect_command_result_contains('/start', [await self.get_response(RK.BASIC_MESSAGE)])

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_start_invalid_command(self):
        await self.expect_command_result_contains(
            '/start nieistniejace_polecenie', [await self.get_response(RK.INVALID_COMMAND_MESSAGE)],
        )

    @pytest.mark.asyncio
    async def test_start_list_command(self):
        await self.expect_command_result_contains('/start lista', [await self.get_response(RK.LIST_MESSAGE)])

    @pytest.mark.asyncio
    async def test_start_search_section(self):
        await self.expect_command_result_contains('/start wyszukiwanie', [await self.get_response(RK.SEARCH_MESSAGE)])

    @pytest.mark.asyncio
    async def test_start_edit_section(self):
        await self.expect_command_result_contains('/start edycja', [await self.get_response(RK.EDIT_MESSAGE)])

    @pytest.mark.asyncio
    async def test_start_management_section(self):
        await self.expect_command_result_contains('/start zarzadzanie', [await self.get_response(RK.MANAGEMENT_MESSAGE)])

    @pytest.mark.asyncio
    async def test_start_reporting_section(self):
        await self.expect_command_result_contains('/start raportowanie', [await self.get_response(RK.REPORTING_MESSAGE)])

    @pytest.mark.asyncio
    async def test_start_subscriptions_section(self):
        await self.expect_command_result_contains('/start subskrypcje', [await self.get_response(RK.SUBSCRIPTIONS_MESSAGE)])

    @pytest.mark.asyncio
    async def test_start_all_commands(self):
        await self.expect_command_result_contains('/start wszystko', [await self.get_response(RK.ALL_MESSAGE)])

    @pytest.mark.asyncio
    async def test_start_shortcuts(self):
        await self.expect_command_result_contains('/start skroty', [await self.get_response(RK.SHORTCUTS_MESSAGE)])
