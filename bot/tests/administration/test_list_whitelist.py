import pytest

from bot.database.database_manager import DatabaseManager
from bot.database.models import UserProfile
from bot.responses.administration.list_whitelist_handler_responses import create_whitelist_response
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestListWhitelistCommand(BaseTest):

    @pytest.fixture(autouse=True)
    def setup_client(self, telegram_client):
        self.client = telegram_client

    @pytest.mark.asyncio
    async def test_list_whitelist_with_users(self):
        await DatabaseManager.add_user(
            user_id=123456,
            username="test_user1",
            full_name="Test User 1",
            note=None,
            subscription_days=None,
        )
        await DatabaseManager.add_user(
            user_id=789012,
            username="test_user2",
            full_name="Test User 2",
            note=None,
            subscription_days=None,
        )

        users = [
            UserProfile(
                user_id=s.DEFAULT_ADMIN,
                username=s.ADMIN_USERNAME,
                full_name=s.ADMIN_FULL_NAME,
                subscription_end=None,
                note=None,
            ),
            UserProfile(
                user_id=123456,
                username="test_user1",
                full_name="Test User 1",
                subscription_end=None,
                note=None,
            ),
            UserProfile(
                user_id=789012,
                username="test_user2",
                full_name="Test User 2",
                subscription_end=None,
                note=None,
            ),
        ]
        await self.expect_command_result_contains('/listwhitelist', [create_whitelist_response(users)])
