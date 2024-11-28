from datetime import date

import pytest

import bot.responses.administration.subscription_status_handler_responses as msg
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSubscriptionCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_subscription_with_active_subscription(self):
        await self.add_test_admin_user()
        await self.send_command(f'/addsubscription {s.DEFAULT_ADMIN} 30')
        expected_end_date = date.today().replace(day=27, month=12, year=2024)

        await self.expect_command_result_contains(
            '/subskrypcja',
            [msg.format_subscription_status_response(str(s.DEFAULT_ADMIN), expected_end_date, 30)],
        )
        await self.send_command(f'/removesubscription {s.DEFAULT_ADMIN}')

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_subscription_without_subscription(self):
        await self.add_test_admin_user()
        await self.send_command(f'/removesubscription {s.DEFAULT_ADMIN}')
        await self.expect_command_result_contains(
            '/subskrypcja',
            [msg.get_no_subscription_message()],
        )
