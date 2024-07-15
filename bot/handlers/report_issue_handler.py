import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.handlers.responses.report_issue_handler_responses import (
    get_log_no_report_content_message,
    get_log_report_received_message,
    get_no_report_content_message,
    get_report_received_message,
)
from bot.utils.database import DatabaseManager


class ReportIssueHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['report', 'zgłoś', 'zglos', 'r']

    async def _do_handle(self, message: Message) -> None:
        username = message.from_user.username

        report_content = message.text.split(maxsplit=1)
        if len(report_content) < 2:
            return await self.__reply_no_report_content(message, username)

        await self.__handle_user_report_submission(message, username, report_content[1])

    async def __reply_no_report_content(self, message: Message, username: str) -> None:
        await message.answer(get_no_report_content_message())
        await self._log_system_message(logging.INFO, get_log_no_report_content_message(username))

    async def __handle_user_report_submission(self, message: Message, username: str, report: str) -> None:
        await DatabaseManager.add_report(username, report)
        await message.answer(get_report_received_message())
        await self._log_system_message(logging.INFO, get_log_report_received_message(username, report))
