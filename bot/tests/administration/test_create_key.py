import pytest

import bot.responses.administration.create_key_handler_responses as create_key_msg
import bot.responses.administration.remove_key_handler_responses as remove_key_msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestAddKeyCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_add_key_valid(self):
        await self.send_command('/removekey tajny_klucz')
        await self.expect_command_result_contains(
            '/addkey 30 tajny_klucz',
            [create_key_msg.get_create_key_success_message(30, "tajny_klucz")],
        )
        await self.expect_command_result_contains(
            '/removekey tajny_klucz',
            [remove_key_msg.get_remove_key_success_message("tajny_klucz")],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_add_key_zero_days(self):
        await self.send_command('/removekey klucz_na_zero_dni')
        await self.expect_command_result_contains(
            '/addkey 0 klucz_na_zero_dni',
            [create_key_msg.get_create_key_success_message(0, "klucz_na_zero_dni")],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_key_negative_days(self):
        await self.send_command('/removekey klucz_na_ujemne_dni')
        await self.expect_command_result_contains(
            '/addkey -30 klucz_na_ujemne_dni',
            [create_key_msg.get_create_key_success_message(-30, "klucz_na_ujemne_dni")],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_key_invalid_days_format(self):
        await self.expect_command_result_contains(
            '/addkey trzydzieści klucz_tekstowy_dni',
            [create_key_msg.get_create_key_usage_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_key_empty_note(self):
        await self.expect_command_result_contains(
            '/addkey 30',
            [create_key_msg.get_create_key_usage_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_key_special_characters_in_note(self):
        await self.expect_command_result_contains(
            '/addkey 30 specjalny@klucz#!',
            [create_key_msg.get_create_key_success_message(30, "specjalny@klucz#!")],
        )
        await self.expect_command_result_contains(
            '/removekey specjalny@klucz#!',
            [remove_key_msg.get_remove_key_success_message("specjalny@klucz#!")],
        )
