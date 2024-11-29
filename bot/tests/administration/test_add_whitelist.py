import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.add_whitelist_handler_responses as add_msg
import bot.responses.administration.remove_whitelist_handler_responses as remove_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestWhitelistCommands(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_add_and_remove_valid_user_whitelist(self):
        user_id = 123456789
        await DatabaseManager.add_user(
            user_id=user_id,
            username="valid_user",
            full_name="Valid User",
            note=None,
            subscription_days=None,
        )

        await self.expect_command_result_contains(
            f'/addwhitelist {user_id}',
            [add_msg.get_user_added_message(str(user_id))],
        )
        await self.expect_command_result_contains(
            f'/removewhitelist {user_id}',
            [remove_msg.get_user_removed_message(str(user_id))],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_add_nonexistent_user_whitelist(self):
        user_id = 999999999
        await self.expect_command_result_contains(
            f'/addwhitelist {user_id}',
            [add_msg.get_user_added_message(str(user_id))],
        )
        await self.expect_command_result_contains(
            f'/removewhitelist {user_id}',
            [remove_msg.get_user_removed_message(str(user_id))],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_whitelist_invalid_user_id_format(self):
        user_id_invalid = "user123"
        await self.expect_command_result_contains(
            f'/addwhitelist {user_id_invalid}',
            [add_msg.get_no_user_id_provided_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_remove_nonexistent_user_whitelist(self):
        user_id = 888888888
        await self.expect_command_result_contains(
            f'/removewhitelist {user_id}',
            [remove_msg.get_user_removed_message(str(user_id))],
        )
