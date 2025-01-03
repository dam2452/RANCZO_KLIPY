import logging
from typing import List

from aiogram.types import Message

from bot.database.database_manager import DatabaseManager
from bot.database.response_keys import ResponseKey as RK
from bot.handlers.bot_message_handler import (
    BotMessageHandler,
    ValidatorFunctions,
)
from bot.responses.administration.report_issue_handler_responses import get_log_report_received_message
from bot.settings import settings


class ReportIssueHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ["report", "zgłoś", "zglos", "r"]

    def _get_validator_functions(self) -> ValidatorFunctions:
        return [
            self.__check_argument_count,
            self.__check_report_length,
        ]

    async def __check_argument_count(self, message: Message) -> bool:
        return await self._validate_argument_count(
            message, 2, await self.get_response(RK.NO_REPORT_CONTENT),
        )


    async def __check_report_length(self,message: Message) -> bool:
        report_content = message.text.split(maxsplit=1)
        if len(report_content[1]) > settings.MAX_REPORT_LENGTH:
            await self._answer(message,await self.get_response(RK.LIMIT_EXCEEDED_REPORT_LENGTH))
            return False
        return True

    async def _do_handle(self, message: Message) -> None:
        report_content = message.text.split(maxsplit=1)[1]
        await self.__handle_user_report_submission(message, report_content)

    async def __handle_user_report_submission(self, message: Message, report: str) -> None:
        await DatabaseManager.add_report(message.from_user.id, report)
        await self._answer(message,await self.get_response(RK.REPORT_RECEIVED))
        await self._log_system_message(logging.INFO, get_log_report_received_message(message.from_user.username, report))
