import logging
from typing import List

from aiogram.types import Message
from tabulate import tabulate

from bot_message_handler import BotMessageHandler
from bot.utils.responses import get_whitelist_empty_message
from bot.utils.database import DatabaseManager

class ListWhitelistHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return ['listwhitelist', 'listw']

    async def _do_handle(self, message: Message) -> None:
        await self._log_user_activity(message.from_user.username, "/listwhitelist")
        users = await DatabaseManager.get_all_users()
        if not users:
            await message.answer(get_whitelist_empty_message())
            await self._log_system_message(logging.INFO, "Whitelist is empty.")
            return

        table = [["Username", "Full Name", "Email", "Phone", "Subskrypcja do"]]
        for user in users:
            table.append([user['username'], user['full_name'], user['email'], user['phone'], user['subscription_end']])

        response = f"```whitelista\n{tabulate(table, headers='firstrow', tablefmt='grid')}```"
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(logging.INFO, "Whitelist sent to user.")

