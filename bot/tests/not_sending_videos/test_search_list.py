import pytest

from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestListCommand(BaseTest):

    @pytest.mark.quick
    async def test_list_after_search(self):
        await self.expect_command_result_contains('/szukaj krowa', ["Znaleziono"])
        response_list = await self.send_command('/lista')
        self.assert_file_matches(response_list, 'expected_list.txt', '.txt')
