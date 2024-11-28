import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.remove_subscription_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestRemoveSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_existing_subscription(self):
        await DatabaseManager.add_user(
            user_id=2015344951,
            username="test_user",
            full_name="Test User",
            note=None,
            subscription_days=30,
        )
        await self.expect_command_result_contains(
            '/removesubscription 2015344951',
            [msg.get_subscription_removed_message("2015344951")],
        )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_remove_nonexistent_subscription(self):
        await self.expect_command_result_contains(
            '/removesubscription 987654321',
            [msg.get_subscription_removed_message("987654321")],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_remove_subscription_twice(self):
        await DatabaseManager.add_user(
            user_id=2015344951,
            username="test_user",
            full_name="Test User",
            note=None,
            subscription_days=30,
        )
        await self.expect_command_result_contains(
            '/removesubscription 2015344951',
            [msg.get_subscription_removed_message("2015344951")],
        )
        await self.expect_command_result_contains(
            '/removesubscription 2015344951',
            [msg.get_subscription_removed_message("2015344951")],
        )

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_remove_subscription_invalid_user_id_format(self):
        await self.expect_command_result_contains(
            '/removesubscription user123',
            [msg.get_no_user_id_provided_message()],
        )
