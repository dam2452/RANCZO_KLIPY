import pytest

from bot.database.database_manager import DatabaseManager
from bot.tests.base_test import BaseTest
# import bot.responses.administration.add_whitelist_handler_responses as add_msg
# import bot.responses.administration.remove_whitelist_handler_responses as remove_msg


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestWhitelistCommands(BaseTest):
    pass
    # @pytest.mark.quick
    # @pytest.mark.asyncio
    # async def test_add_and_remove_valid_user_whitelist(self):
    #     user_id = 123456789
    #     await DatabaseManager.add_user(
    #         user_id=user_id,
    #         username="valid_user",
    #         full_name="Valid User",
    #         note=None,
    #         subscription_days=None,
    #     )
    #
    #     await self.expect_command_result_contains(
    #         f'/addwhitelist {user_id}',
    #         [add_msg.get_user_added_message("valid_user")],
    #     )
    #     await self.expect_command_result_contains(
    #         f'/removewhitelist {user_id}',
    #         [remove_msg.get_user_removed_message(str(user_id))],
    #     )
    #
    # @pytest.mark.quick
    # @pytest.mark.asyncio
    # async def test_add_nonexistent_user_whitelist(self):
    #     user_id = 99999999999
    #     await self.expect_command_result_contains(
    #         f'/addwhitelist {user_id}',
    #         [add_msg.get_user_not_found_message()],
    #     )
    #
    # @pytest.mark.asyncio
    # async def test_add_whitelist_invalid_user_id_format(self):
    #     user_id_invalid = "invalid_id"
    #     await self.expect_command_result_contains(
    #         f'/addwhitelist {user_id_invalid}',
    #         [add_msg.get_no_user_id_provided_message()],
    #     )
    #
    # @pytest.mark.asyncio
    # async def test_add_user_with_no_username(self):
    #     user_id = 888888888
    #     await DatabaseManager.add_user(
    #         user_id=user_id,
    #         username=None,
    #         full_name="User Without Username",
    #         note=None,
    #         subscription_days=None,
    #     )
    #
    #     await self.expect_command_result_contains(
    #         f'/addwhitelist {user_id}',
    #         [add_msg.get_user_added_message("User Without Username")],
    #     )
