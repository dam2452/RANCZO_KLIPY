import pytest

from bot.database.database_manager import DatabaseManager
from bot.database.models import UserProfile
from bot.responses.administration.list_moderators_handler_responses import format_moderators_list
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestListModeratorsCommand(BaseTest):
    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_list_moderators_with_moderators(self):
        await DatabaseManager.add_user(user_id=123456, username="moderator1", full_name="Moderator One", note=None)
        await DatabaseManager.add_user(user_id=789012, username="moderator2", full_name="Moderator Two", note=None)

        await DatabaseManager.set_user_as_moderator(user_id=123456)
        await DatabaseManager.set_user_as_moderator(user_id=789012)

        moderators = [
            UserProfile(user_id=123456, username="moderator1", full_name="Moderator One", subscription_end=None, note=None),
            UserProfile(user_id=789012, username="moderator2", full_name="Moderator Two", subscription_end=None, note=None),
        ]

        await self.expect_command_result_contains(
            '/listmoderators',
            [format_moderators_list(moderators)],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_list_moderators_empty(self):
        await self.expect_command_result_contains(
            '/listmoderators',
            ["Brak moderatorów na liście."],
        )
