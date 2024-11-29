import pytest

from bot.database.database_manager import DatabaseManager
from bot.database.models import UserProfile
from bot.responses.administration.list_moderators_handler_responses import (
    format_moderators_list,
    get_no_moderators_found_message,
)
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestListModeratorsCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_list_moderators_with_moderators(self):
        user1 = {
            "user_id": 123456,
            "username": "moderator1",
            "full_name": "Moderator One",
            "note": "Test note",
            "subscription_end": None,
        }
        user2 = {
            "user_id": 789012,
            "username": "moderator2",
            "full_name": "Moderator Two",
            "note": "Another test note",
            "subscription_end": None,
        }

        await DatabaseManager.add_user(
            user_id=user1["user_id"],
            username=user1["username"],
            full_name=user1["full_name"],
            note=user1["note"],
            subscription_days=None,
        )
        await DatabaseManager.add_user(
            user_id=user2["user_id"],
            username=user2["username"],
            full_name=user2["full_name"],
            note=user2["note"],
            subscription_days=None,
        )

        await DatabaseManager.set_user_as_moderator(user_id=user1["user_id"])
        await DatabaseManager.set_user_as_moderator(user_id=user2["user_id"])

        moderators = [
            UserProfile(
                user_id=user1["user_id"],
                username=user1["username"],
                full_name=user1["full_name"],
                note=user1["note"],
                subscription_end=user1["subscription_end"],
            ),
            UserProfile(
                user_id=user2["user_id"],
                username=user2["username"],
                full_name=user2["full_name"],
                note=user2["note"],
                subscription_end=user2["subscription_end"],
            ),
        ]

        await self.expect_command_result_contains(
            '/listmoderators', [format_moderators_list(moderators)],
        )

    @pytest.mark.asyncio
    async def test_list_moderators_empty(self):
        await self.expect_command_result_contains(
            '/listmoderators', [get_no_moderators_found_message()],
        )
