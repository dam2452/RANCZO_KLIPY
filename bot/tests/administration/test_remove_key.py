import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.remove_key_handler_responses as remove_key_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestRemoveKeyCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_existing_key(self):
        await DatabaseManager.create_subscription_key(30, "tajny_klucz")
        await self.expect_command_result_contains(
            '/removekey tajny_klucz',
            [remove_key_msg.get_remove_key_success_message("tajny_klucz")],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_nonexistent_key(self):
        await self.expect_command_result_contains(
            '/removekey nieistniejacy_klucz',
            [remove_key_msg.get_remove_key_failure_message("nieistniejacy_klucz")],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_remove_key_with_special_characters(self):
        await DatabaseManager.create_subscription_key(30, "specjalny@klucz#!")
        await self.expect_command_result_contains(
            '/removekey specjalny@klucz#!',
            [remove_key_msg.get_remove_key_success_message("specjalny@klucz#!")],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_remove_key_twice(self):
        await DatabaseManager.create_subscription_key(30, "klucz_do_usuniecia")
        await self.expect_command_result_contains(
            '/removekey klucz_do_usuniecia',
            [remove_key_msg.get_remove_key_success_message("klucz_do_usuniecia")],
        )
        await self.expect_command_result_contains(
            '/removekey klucz_do_usuniecia',
            [remove_key_msg.get_remove_key_failure_message("klucz_do_usuniecia")],
        )
