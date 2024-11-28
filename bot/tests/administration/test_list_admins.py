

import pytest

from bot.database.database_manager import DatabaseManager
from bot.database.models import UserProfile
import bot.responses.administration.list_admins_handler_responses as msg
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestListAdminsCommand(BaseTest):

    @pytest.fixture(autouse=True)
    def setup_client(self, telegram_client):
        self.client = telegram_client

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_list_admins_with_admins(self):
        await DatabaseManager.add_user(
            user_id=s.DEFAULT_ADMIN,
            username=s.ADMIN_USERNAME,
            full_name=s.ADMIN_FULL_NAME,
            note=None,
            subscription_days=None,
        )

        admins = [
            UserProfile(
                user_id=s.DEFAULT_ADMIN,
                username=s.ADMIN_USERNAME,
                full_name=s.ADMIN_FULL_NAME,
                subscription_end=None,
                note=None,
            ),
        ]

        await self.expect_command_result_contains('/listadmins', [msg.format_admins_list(admins)])
