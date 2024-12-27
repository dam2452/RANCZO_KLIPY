from datetime import (
    date,
    timedelta,
)

import pytest

import bot.responses.administration.subscription_status_handler_responses as msg
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSubscriptionCommand(BaseTest):

    @pytest.mark.asyncio
    async def test_subscription_with_active_subscription(self):
        days = 30
        end_date = date.today() + timedelta(days=days)
        await self.send_command(f'/addsubscription {s.DEFAULT_ADMIN} {days}')
        expected_response = msg.format_subscription_status_response(
            s.TESTER_USERNAME, end_date, days,
        )

        await self.expect_command_result_contains('/subskrypcja', [expected_response])
        await self.send_command(f'/removesubscription {s.DEFAULT_ADMIN}')

    @pytest.mark.asyncio
    async def test_subscription_without_subscription(self):
        await self.add_test_admin_user()
        await self.send_command(f'/removesubscription {s.DEFAULT_ADMIN}')
        await self.expect_command_result_contains(
            '/subskrypcja', [msg.get_no_subscription_message()],
        )

    @pytest.mark.asyncio
    async def test_subscription_with_expired_subscription(self):
        await self.expect_command_result_contains(
            '/subskrypcja', [msg.get_no_subscription_message()],
        )

    @pytest.mark.asyncio
    async def test_subscription_long_duration(self):
        await self.add_test_admin_user()
        long_duration = 365 * 2
        end_date = date.today() + timedelta(days=long_duration)
        await self.send_command(f'/addsubscription {s.DEFAULT_ADMIN} {long_duration}')
        expected_response = msg.format_subscription_status_response(
            s.TESTER_USERNAME, end_date, long_duration,
        )

        await self.expect_command_result_contains('/subskrypcja', [expected_response])

    @pytest.mark.asyncio
    async def test_subscription_invalid_user(self):
        invalid_user_id = 99999
        response = await self.send_command(f'/subskrypcja {invalid_user_id}')
        self.assert_response_contains(response, [msg.get_no_subscription_message()])
