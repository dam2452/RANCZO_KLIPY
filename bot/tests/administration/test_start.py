import pytest

import bot.responses.administration.start_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestStartCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_start_base_command(self):
        await self.expect_command_result_contains('/start', [self.remove_until_first_space(msg.get_basic_message())])

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_start_invalid_command(self):
        await self.expect_command_result_contains(
            '/start nieistniejace_polecenie', [self.remove_until_first_space(msg.get_invalid_command_message())],
        )

    @pytest.mark.asyncio
    async def test_start_list_command(self):
        await self.expect_command_result_contains('/start lista', [self.remove_until_first_space(msg.get_list_message())])

    @pytest.mark.asyncio
    async def test_start_search_section(self):
        await self.expect_command_result_contains('/start wyszukiwanie', [self.remove_until_first_space(msg.get_search_message())])

    @pytest.mark.asyncio
    async def test_start_edit_section(self):
        await self.expect_command_result_contains('/start edycja', [self.remove_until_first_space(msg.get_edit_message())])

    @pytest.mark.asyncio
    async def test_start_management_section(self):
        await self.expect_command_result_contains('/start zarzadzanie', [self.remove_until_first_space(msg.get_menagement_message())])

    @pytest.mark.asyncio
    async def test_start_reporting_section(self):
        await self.expect_command_result_contains('/start raportowanie', [self.remove_until_first_space(msg.get_reporting_message())])

    @pytest.mark.asyncio
    async def test_start_subscriptions_section(self):
        await self.expect_command_result_contains('/start subskrypcje', [self.remove_until_first_space(msg.get_subscriptions_message())])

    @pytest.mark.asyncio
    async def test_start_all_commands(self):
        await self.expect_command_result_contains('/start wszystko', [self.remove_until_first_space(msg.get_all_message())])

    @pytest.mark.asyncio
    async def test_start_shortcuts(self):
        await self.expect_command_result_contains('/start skroty', [self.remove_until_first_space(msg.get_shortcuts_message())])
