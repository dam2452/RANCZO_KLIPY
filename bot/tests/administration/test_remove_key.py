import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.remove_key_handler_responses as remove_key_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestRemoveKeyCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_existing_key(self):
        key = "tajny_klucz"
        await DatabaseManager.create_subscription_key(30, key)
        await self.expect_command_result_contains(
            f'/removekey {key}',
            [remove_key_msg.get_remove_key_success_message(key)],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_nonexistent_key(self):
        key = "nieistniejacy_klucz"
        await self.expect_command_result_contains(
            f'/removekey {key}',
            [remove_key_msg.get_remove_key_failure_message(key)],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_remove_key_with_special_characters(self):
        key = "specjalny@klucz#!"
        await DatabaseManager.create_subscription_key(30, key)
        await self.expect_command_result_contains(
            f'/removekey {key}',
            [remove_key_msg.get_remove_key_success_message(key)],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_remove_key_twice(self):
        key = "klucz_do_usuniecia"
        await DatabaseManager.create_subscription_key(30, key)
        await self.expect_command_result_contains(
            f'/removekey {key}',
            [remove_key_msg.get_remove_key_success_message(key)],
        )
        await self.expect_command_result_contains(
            f'/removekey {key}',
            [remove_key_msg.get_remove_key_failure_message(key)],
        )
