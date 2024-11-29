from datetime import (
    date,
    timedelta,
)

import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.add_subscription_handler_responses as msg
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestAddSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_add_subscription_valid_user(self):
        user_id = 123456789
        days = 30

        await DatabaseManager.add_user(
            user_id=user_id,
            username="test_user",
            full_name="Test User",
            note=None,
            subscription_days=None,
        )

        expected_end_date = date.today() + timedelta(days=days)

        await self.expect_command_result_contains(
            f'/addsubscription {user_id} {days}',
            [msg.get_subscription_extended_message(str(user_id), expected_end_date)],
        )

    @pytest.mark.asyncio
    async def test_add_subscription_existing_admin(self):
        days = 60
        expected_end_date = date.today() + timedelta(days=days)

        await self.expect_command_result_contains(
            f'/addsubscription {s.DEFAULT_ADMIN} {days}',
            [msg.get_subscription_extended_message(str(s.DEFAULT_ADMIN), expected_end_date)],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_add_subscription_nonexistent_user(self):
        user_id = 999999999
        days = 30

        await self.expect_command_result_contains(
            f'/addsubscription {user_id} {days}',
            [msg.get_subscription_error_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_subscription_invalid_days_format(self):
        user_id = 123456789
        invalid_days = "trzydzieści"

        await self.expect_command_result_contains(
            f'/addsubscription {user_id} {invalid_days}',
            [msg.get_no_user_id_provided_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_subscription_invalid_user_id_format(self):
        user_id_invalid = "user123"
        days = 30

        await self.expect_command_result_contains(
            f'/addsubscription {user_id_invalid} {days}',
            [msg.get_no_user_id_provided_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_subscription_negative_days(self):
        user_id = 123456789
        negative_days = -30

        await self.expect_command_result_contains(
            f'/addsubscription {user_id} {negative_days}',
            [msg.get_no_user_id_provided_message()],
        )
