import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.remove_whitelist_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestRemoveWhitelistCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_existing_user_whitelist(self):
        user_id = 6967485026
        await DatabaseManager.add_user(
            user_id=user_id,
            username="test_user",
            full_name="Test User",
            note=None,
            subscription_days=None,
        )
        await self.expect_command_result_contains(
            f'/removewhitelist {user_id}',
            [msg.get_user_removed_message(str(user_id))],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_nonexistent_user_whitelist(self):
        user_id = 6967485026
        await self.expect_command_result_contains(
            f'/removewhitelist {user_id}',
            [msg.get_user_not_in_whitelist_message(str(user_id))],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_remove_user_whitelist_twice(self):
        user_id = 123456789
        await DatabaseManager.add_user(
            user_id=user_id,
            username="test_user2",
            full_name="Test User 2",
            note=None,
            subscription_days=None,
        )
        await self.expect_command_result_contains(
            f'/removewhitelist {user_id}',
            [msg.get_user_removed_message(str(user_id))],
        )
        await self.expect_command_result_contains(
            f'/removewhitelist {user_id}',
            [msg.get_user_not_in_whitelist_message(str(user_id))],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_remove_whitelist_invalid_user_id_format(self):
        await self.expect_command_result_contains(
            '/removewhitelist user123',
            [msg.get_no_user_id_provided_message()],
        )
