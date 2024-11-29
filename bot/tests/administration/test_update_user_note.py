import pytest

import bot.responses.administration.update_user_note_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestUpdateUserNoteCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_add_note_with_valid_user_and_content(self):
        user = await self.add_test_user()
        await self.expect_command_result_contains(
            f'/note {user["user_id"]} notatka123',
            [msg.get_note_updated_message()],
        )

    @pytest.mark.asyncio
    async def test_note_missing_user_id_and_content(self):
        response = await self.send_command('/note')
        self.assert_response_contains(response, [msg.get_no_note_provided_message()])

    @pytest.mark.asyncio
    async def test_note_missing_content(self):
        user = await self.add_test_user()
        response = await self.send_command(f'/note {user["user_id"]}')
        self.assert_response_contains(response, [msg.get_no_note_provided_message()])

    @pytest.mark.asyncio
    async def test_note_with_special_characters_in_content(self):
        user = await self.add_test_user()
        await self.expect_command_result_contains(
            f'/note {user["user_id"]} notatka@#!$%&*()',
            [msg.get_note_updated_message()],
        )

    @pytest.mark.asyncio
    async def test_note_with_invalid_user_id_format(self):
        response = await self.send_command('/note user123 notatka_testowa')
        self.assert_response_contains(response, [msg.get_invalid_user_id_message("user123")])

    @pytest.mark.asyncio
    async def test_note_with_long_content(self):
        user = await self.add_test_user()
        long_content = "to jest bardzo długa notatka " * 20
        await self.expect_command_result_contains(
            f'/note {user["user_id"]} {long_content}',
            [msg.get_note_updated_message()],
        )

    @pytest.mark.asyncio
    async def test_update_existing_note(self):
        user = await self.add_test_user()
        await self.expect_command_result_contains(
            f'/note {user["user_id"]} pierwsza_notatka',
            [msg.get_note_updated_message()],
        )
        await self.expect_command_result_contains(
            f'/note {user["user_id"]} druga_notatka',
            [msg.get_note_updated_message()],
        )
