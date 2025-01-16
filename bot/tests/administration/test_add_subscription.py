from datetime import (
    date,
    timedelta,
)

import pytest

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestAddSubscriptionHandler(BaseTest):

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
            [await self.get_response(RK.SUBSCRIPTION_EXTENDED, [str(user_id), str(expected_end_date)])],
        )

    @pytest.mark.asyncio
    async def test_add_subscription_existing_admin(self):
        days = 60
        expected_end_date = date.today() + timedelta(days=days)

        await self.expect_command_result_contains(
            f'/addsubscription {s.DEFAULT_ADMIN} {days}',
            [await self.get_response(RK.SUBSCRIPTION_EXTENDED, [str(s.DEFAULT_ADMIN), str(expected_end_date)])],
        )


    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_add_subscription_nonexistent_user(self):
        user_id = 999999999
        days = 30

        await self.expect_command_result_contains(
            f'/addsubscription {user_id} {days}',
            [await self.get_response(RK.SUBSCRIPTION_ERROR)],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_subscription_invalid_days_format(self):
        user_id = 123456789
        invalid_days = "trzydzieści"

        await self.expect_command_result_contains(
            f'/addsubscription {user_id} {invalid_days}',
            [await self.get_response(RK.NO_USER_ID_PROVIDED)],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_subscription_invalid_user_id_format(self):
        user_id_invalid = "user123"
        days = 30

        await self.expect_command_result_contains(
            f'/addsubscription {user_id_invalid} {days}',
            [await self.get_response(RK.NO_USER_ID_PROVIDED)],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_add_subscription_negative_days(self):
        user_id = 123456789
        negative_days = -30

        await self.expect_command_result_contains(
            f'/addsubscription {user_id} {negative_days}',
            [await self.get_response(RK.NO_USER_ID_PROVIDED)],
        )
