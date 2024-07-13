import logging
from typing import List

from aiogram.types import Message

from bot.handlers.bot_message_handler import BotMessageHandler
from bot.utils.database import DatabaseManager


class ReportIssueHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['report', 'zgłoś', 'zglos', 'r']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, f"/report {message.text}")
        username = message.from_user.username

        report_content = message.text.split(maxsplit=1)
        if len(report_content) < 2:
            return await self.__reply_no_report_content(message, username)

        await self.__handle_user_report_submission(message, username, report_content[1])

    async def __reply_no_report_content(self, message: Message, username: str) -> None:
        await message.answer("❌ Podaj treść raportu.❌")
        await self._log_system_message(logging.INFO, f"No report content provided by user '{username}'.")

    async def __handle_user_report_submission(self, message: Message, username: str, report: str) -> None:
        await DatabaseManager.add_report(username, report)
        await message.answer("✅ Dziękujemy za zgłoszenie. Twój raport został zapisany. 📄")
        await self._log_system_message(logging.INFO, f"Report received from user '{username}': {report}")
