import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.use_key_handler_responses as use_key_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestUseKeyCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_use_valid_key(self):
        key = "valid_key"
        subscription_days = 30

        await DatabaseManager.create_subscription_key(subscription_days, key)
        await self.expect_command_result_contains(
            f'/klucz {key}',
            [use_key_msg.get_subscription_redeemed_message(subscription_days)],
        )
        await self.expect_command_result_contains(
            f'/klucz {key}',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key(key)

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_use_invalid_key(self):
        key = "invalid_key"

        response = await self.send_command(f'/klucz {key}')
        self.assert_response_contains(response, [use_key_msg.get_invalid_key_message()])

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_use_key_no_arguments(self):
        command = '/klucz'

        response = await self.send_command(command)
        self.assert_response_contains(response, [use_key_msg.get_no_message_provided_message()])

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_use_key_special_characters(self):
        key = "spec!@#_key"
        subscription_days = 30

        await DatabaseManager.create_subscription_key(subscription_days, key)
        await self.expect_command_result_contains(
            f'/klucz {key}',
            [use_key_msg.get_subscription_redeemed_message(subscription_days)],
        )
        await self.expect_command_result_contains(
            f'/klucz {key}',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key(key)

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_use_key_multiple_times(self):
        key = "single_use_key"
        subscription_days = 30

        await DatabaseManager.create_subscription_key(subscription_days, key)
        await self.expect_command_result_contains(
            f'/klucz {key}',
            [use_key_msg.get_subscription_redeemed_message(subscription_days)],
        )
        await self.expect_command_result_contains(
            f'/klucz {key}',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key(key)

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_use_key_edge_case(self):
        key = "key_" + "x" * 100
        subscription_days = 30

        await DatabaseManager.create_subscription_key(subscription_days, key)
        await self.expect_command_result_contains(
            f'/klucz {key}',
            [use_key_msg.get_subscription_redeemed_message(subscription_days)],
        )
        await self.expect_command_result_contains(
            f'/klucz {key}',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key(key)
