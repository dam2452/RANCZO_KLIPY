import pytest

import bot.responses.administration.subscription_status_handler_responses as msg
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestSubscriptionCommand(BaseTest):

    # @pytest.mark.asyncio
    # async def test_subscription_with_active_subscription(self):
    #     await self.add_test_admin_user()
    #     end_date = date.today() + timedelta(days=30)
    #     await self.send_command(f'/addsubscription {s.DEFAULT_ADMIN} 30')
    #     expected_response = msg.format_subscription_status_response(
    #         str(s.DEFAULT_ADMIN), end_date, 30
    #     )
    #
    #     await self.expect_command_result_contains('/subskrypcja', [expected_response])
    #     await self.send_command(f'/removesubscription {s.DEFAULT_ADMIN}')

    @pytest.mark.asyncio
    async def test_subscription_without_subscription(self):
        await self.add_test_admin_user()
        await self.send_command(f'/removesubscription {s.DEFAULT_ADMIN}')
        await self.expect_command_result_contains(
            '/subskrypcja', [msg.get_no_subscription_message()],
        )

    # @pytest.mark.asyncio
    # async def test_subscription_with_expired_subscription(self):
    #     await self.add_test_admin_user()
    #     expired_date = -10
    #     await DatabaseManager.add_subscription(s.DEFAULT_ADMIN, expired_date)
    #     await self.expect_command_result_contains(
    #         '/subskrypcja', [msg.get_no_subscription_message()]
    #     )

    # @pytest.mark.asyncio
    # async def test_subscription_long_duration(self):
    #     await self.add_test_admin_user()
    #     long_duration = 365 * 2
    #     end_date = date.today() + timedelta(days=long_duration)
    #     await self.send_command(f'/addsubscription {s.DEFAULT_ADMIN} {long_duration}')
    #     expected_response = msg.format_subscription_status_response(
    #         str(s.DEFAULT_ADMIN), end_date, long_duration
    #     )
    #
    #     await self.expect_command_result_contains('/subskrypcja', [expected_response])
    #     await self.send_command(f'/removesubscription {s.DEFAULT_ADMIN}')

    @pytest.mark.asyncio
    async def test_subscription_invalid_user(self):
        invalid_user_id = 99999
        response = await self.send_command(f'/subskrypcja {invalid_user_id}')
        self.assert_response_contains(response, [msg.get_no_subscription_message()])
