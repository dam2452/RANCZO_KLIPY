import pytest

import bot.responses.administration.report_issue_handler_responses as msg
from bot.tests.base_test import BaseTest


@pytest.mark.usefixtures("db_pool", "telegram_client")
class TestReportCommand(BaseTest):

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_report_with_valid_message(self):
        message = 'To i to nie działa'
        await self.expect_command_result_contains(f'/report {message}', [msg.get_report_received_message()])

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_report_with_empty_message(self):
        command = '/report'
        await self.expect_command_result_contains(command, [msg.get_no_report_content_message()])

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_report_with_special_characters_in_message(self):
        message = 'To się nie działa @#$%^&*()!'
        await self.expect_command_result_contains(f'/report {message}', [msg.get_report_received_message()])

    @pytest.mark.long
    @pytest.mark.asyncio
    async def test_report_with_long_message(self):
        long_message = "To i to nie działa. " * 20
        await self.expect_command_result_contains(f'/report {long_message}', [msg.get_report_received_message()])
