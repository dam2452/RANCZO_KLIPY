import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.update_user_note_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestNoteCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_add_note_with_valid_user_and_content(self):
        user_id = 2015344951
        await DatabaseManager.add_user(
            user_id=user_id,
            username="test_user",
            full_name="Test User",
            note=None,
            subscription_days=None,
        )
        await self.expect_command_result_contains(
            f'/note {user_id} notatka123',
            [msg.get_note_updated_message()],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_note_missing_user_id_and_content(self):
        await self.expect_command_result_contains(
            '/note',
            [msg.get_no_note_provided_message()],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_note_missing_content(self):
        await self.expect_command_result_contains(
            '/note 2015344951',
            [msg.get_no_note_provided_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_note_with_special_characters_in_content(self):
        user_id = 2015344951
        await DatabaseManager.add_user(
            user_id=user_id,
            username="test_user",
            full_name="Test User",
            note=None,
            subscription_days=None,
        )
        await self.expect_command_result_contains(
            f'/note {user_id} notatka@#!$%&*()',
            [msg.get_note_updated_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_note_with_invalid_user_id_format(self):
        await self.expect_command_result_contains(
            '/note user123 notatka_testowa',
            [msg.get_invalid_user_id_message("user123")],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_note_with_long_content(self):
        user_id = 2015344951
        long_content = "to jest bardzo długa notatka " * 10
        await DatabaseManager.add_user(
            user_id=user_id,
            username="test_user",
            full_name="Test User",
            note=None,
            subscription_days=None,
        )
        await self.expect_command_result_contains(
            f'/note {user_id} {long_content}',
            [msg.get_note_updated_message()],
        )
