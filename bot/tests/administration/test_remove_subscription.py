import pytest

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestRemoveSubscriptionHandler(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_existing_subscription(self):
        user_id = 2015344951
        await DatabaseManager.add_user(
            user_id=user_id,
            username="test_user",
            full_name="Test User",
            note=None,
            subscription_days=30,
        )
        await self.expect_command_result_contains(
            f'/removesubscription {user_id}',
            [await self.get_response(RK.SUBSCRIPTION_REMOVED, [str(user_id)])],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_nonexistent_subscription(self):
        user_id = 987654321
        await self.expect_command_result_contains(
            f'/removesubscription {user_id}',
            [await self.get_response(RK.SUBSCRIPTION_REMOVED, [str(user_id)])],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_subscription_invalid_user_id_format(self):
        await self.expect_command_result_contains(
            '/removesubscription user123',
            [await self.get_response(RK.NO_USER_ID_PROVIDED)],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_remove_subscription_twice(self):
        user_id = 2015344951
        await DatabaseManager.add_user(
            user_id=user_id,
            username="test_user",
            full_name="Test User",
            note=None,
            subscription_days=30,
        )
        await self.expect_command_result_contains(
            f'/removesubscription {user_id}',
            [await self.get_response(RK.SUBSCRIPTION_REMOVED, [str(user_id)])],
        )
        await self.expect_command_result_contains(
            f'/removesubscription {user_id}',
            [await self.get_response(RK.SUBSCRIPTION_REMOVED, [str(user_id)])],
        )
