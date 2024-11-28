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
        await DatabaseManager.add_user(
            user_id=user_id,
            username="test_user",
            full_name="Test User",
            note=None,
            subscription_days=None,
        )

        expected_end_date = date.today() + timedelta(days=30)

        await self.expect_command_result_contains(
            f'/addsubscription {user_id} 30',
            [msg.get_subscription_extended_message(str(user_id), expected_end_date)],
        )

    @pytest.mark.asyncio
    async def test_add_subscription_existing_admin(self):
        expected_end_date = date.today() + timedelta(days=60)

        await self.expect_command_result_contains(
            f'/addsubscription {s.DEFAULT_ADMIN} 60',
            [msg.get_subscription_extended_message(str(s.DEFAULT_ADMIN), expected_end_date)],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_add_subscription_nonexistent_user(self):
        await self.expect_command_result_contains(
            '/addsubscription 999999999 30',
            [msg.get_subscription_error_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_subscription_invalid_days_format(self):
        await self.expect_command_result_contains(
            '/addsubscription 123456789 trzydzieści',
            [msg.get_no_user_id_provided_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_subscription_invalid_user_id_format(self):
        await self.expect_command_result_contains(
            '/addsubscription user123 30',
            [msg.get_no_user_id_provided_message()],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_subscription_negative_days(self):
        await self.expect_command_result_contains(
            '/addsubscription 123456789 -30',
            [msg.get_no_user_id_provided_message()],
        )
