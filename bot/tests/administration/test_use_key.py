import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.use_key_handler_responses as use_key_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestUseKeyCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_use_existing_key(self):
        await DatabaseManager.create_subscription_key(30, "aktywny_klucz")
        await self.expect_command_result_contains(
            '/klucz aktywny_klucz',
            [use_key_msg.get_subscription_redeemed_message(30)],
        )
        await self.expect_command_result_contains(
            '/klucz aktywny_klucz',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key("aktywny_klucz")

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_use_nonexistent_key(self):
        await self.expect_command_result_contains(
            '/klucz nieistniejacy_klucz',
            [use_key_msg.get_invalid_key_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_use_key_with_special_characters(self):
        await DatabaseManager.create_subscription_key(30, "spec@l_key!")
        await self.expect_command_result_contains(
            '/klucz spec@l_key!',
            [use_key_msg.get_subscription_redeemed_message(30)],
        )
        await self.expect_command_result_contains(
            '/klucz spec@l_key!',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key("spec@l_key!")

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_use_key_twice(self):
        await DatabaseManager.create_subscription_key(30, "klucz_jednorazowy")
        await self.expect_command_result_contains(
            '/klucz klucz_jednorazowy',
            [use_key_msg.get_subscription_redeemed_message(30)],
        )
        await self.expect_command_result_contains(
            '/klucz klucz_jednorazowy',
            [use_key_msg.get_invalid_key_message()],
        )
        await DatabaseManager.remove_subscription_key("klucz_jednorazowy")

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_use_key_without_content(self):
        await self.expect_command_result_contains(
            '/klucz',
            [use_key_msg.get_no_message_provided_message()],
        )
