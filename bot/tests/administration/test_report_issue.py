import pytest

from bot.database.database_manager import DatabaseManager
import bot.responses.administration.report_issue_handler_responses as msg
from bot.tests.base_test import BaseTest
from bot.tests.settings import settings as s


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

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_report_with_special_characters_in_message(self):
        message = 'To się nie działa @#$%^&*()!'
        await self.expect_command_result_contains(f'/report {message}', [msg.get_report_received_message()])

    # @pytest.mark.quick
    # @pytest.mark.asyncio
    # async def test_report_with_long_message(self):
    #     long_message = "To i to nie działa. " * 4000
    #     await self.expect_command_result_contains(
    #         f'/report {long_message}',
    #         [msg.get_limit_exceeded_report_length_message()]
    #     )

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_report_with_alias_command(self):
        message = 'Alias działa poprawnie'
        await self.expect_command_result_contains(f'/r {message}', [msg.get_report_received_message()])

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_report_with_multiple_spaces(self):
        message = '   To się nie działa   '
        await self.expect_command_result_contains(f'/report {message}', [msg.get_report_received_message()])

    @pytest.mark.quick
    @pytest.mark.asyncio
    async def test_report_logs(self):
        message = 'To i to nie działa'

        await self.expect_command_result_contains(f'/report {message}', [msg.get_report_received_message()])

        reports = await DatabaseManager.get_reports(s.DEFAULT_ADMIN)

        assert len(reports) > 0, "Zgłoszenie nie zostało zapisane w bazie danych."
        assert reports[0]['report'] == message, f"Oczekiwano: {message}, otrzymano: {reports[0]['report']}"
