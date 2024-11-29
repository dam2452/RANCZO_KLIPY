import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.use_key_handler_responses as use_key_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestUseKeyCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_use_valid_key(self):
        await DatabaseManager.create_subscription_key(30, "valid_key")
        await self.expect_command_result_contains(
            '/klucz valid_key',
            [use_key_msg.get_subscription_redeemed_message(30)],
        )
        await self.expect_command_result_contains(
            '/klucz valid_key',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key("valid_key")

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_use_invalid_key(self):
        response = await self.send_command('/klucz invalid_key')
        self.assert_response_contains(response, [use_key_msg.get_invalid_key_message()])

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_use_key_no_arguments(self):
        response = await self.send_command('/klucz')
        self.assert_response_contains(response, [use_key_msg.get_no_message_provided_message()])

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_use_key_special_characters(self):
        special_key = "spec!@#_key"
        await DatabaseManager.create_subscription_key(30, special_key)
        await self.expect_command_result_contains(
            f'/klucz {special_key}',
            [use_key_msg.get_subscription_redeemed_message(30)],
        )
        await self.expect_command_result_contains(
            f'/klucz {special_key}',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key(special_key)

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_use_key_multiple_times(self):
        key = "single_use_key"
        await DatabaseManager.create_subscription_key(30, key)
        await self.expect_command_result_contains(
            f'/klucz {key}',
            [use_key_msg.get_subscription_redeemed_message(30)],
        )
        await self.expect_command_result_contains(
            f'/klucz {key}',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key(key)

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_use_key_edge_case(self):
        long_key = "key_" + "x" * 100
        await DatabaseManager.create_subscription_key(30, long_key)
        await self.expect_command_result_contains(
            f'/klucz {long_key}',
            [use_key_msg.get_subscription_redeemed_message(30)],
        )
        await self.expect_command_result_contains(
            f'/klucz {long_key}',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key(long_key)
