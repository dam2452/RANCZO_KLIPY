import logging
from typing import (
    Callable,
    Dict,
    List,
    Optional,
)

from aiogram import Bot
from aiogram.types import Message
import asyncpg
from tabulate import tabulate

from bot.handlers.bot_message_handler import (
    BaseMiddleware,
    BotMessageHandler,
)
from bot.utils.database import DatabaseManager
from bot.utils.responses import (
    get_admin_help_message,
    get_no_admins_found_message,
    get_no_moderators_found_message,
    get_no_quote_provided_message,
    get_no_segments_found_message,
    get_no_username_provided_message,
    get_subscription_extended_message,
    get_subscription_removed_message,
    get_transcription_response,
    get_user_added_message,
    get_user_removed_message,
    get_user_updated_message,
    get_whitelist_empty_message,
)
from bot.utils.transcription_search import SearchTranscriptions


# fixme: ta klasa po prostu powinna zostac rozbita na add whitelist handler, remove whitelist handler etc.... a z niej zostawić jedynie admin help
# fixme: wtedy tez zniknie potrzeba _ argow z dupy
# fixme: po prostu kazda z funkcji wymieniona w inicie powinna byc osobna -- jak rozbijesz zrobie review
class AdminCommandHandler(BotMessageHandler):
    def __init__(self, bot: Bot, middlewares: Optional[List[BaseMiddleware]] = None):
        self.__HANDLES: Dict[str, Callable[[Message, List[str]], None]] = {
            "addwhitelist": self.__add_to_whitelist,
            "addw": self.__add_to_whitelist,
            "removewhitelist": self.__remove_from_whitelist,
            "removew": self.__remove_from_whitelist,
            "updatewhitelist": self.__update_whitelist,
            "updatew": self.__update_whitelist,
            "listwhitelist": self.__list_whitelist,
            "listw": self.__list_whitelist,
            "listadmins": self.__list_admins,
            "listad": self.__list_admins,
            "listmoderators": self.__list_moderators,
            "listmod": self.__list_moderators,
            "addsubscription": self.__add_subscription_command,
            "addsub": self.__add_subscription_command,
            "removesubscription": self.__remove_subscription_command,
            "removesub": self.__remove_subscription_command,
            "transkrypcja": self.__handle_transcription_request,
            "trans": self.__handle_transcription_request,
        }

        super().__init__(bot, middlewares)

    def get_commands(self) -> List[str]:
        return list(self.__HANDLES.keys())

    async def _do_handle(self, message: Message) -> None:
        username = message.from_user.username
        if not await DatabaseManager.is_user_admin(username) and not await DatabaseManager.is_user_moderator(username):
            await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.❌")
            return await self._log_system_message(logging.WARNING, f"Unauthorized access attempt by user: {username}")

        command = message.get_command(pure=True)
        content = message.text.split()[1:]

        if command == 'admin':
            await message.answer(get_admin_help_message(), parse_mode='Markdown')  # fixme tutaj docelowo zostaje tylko to xD
        else:
            self.__HANDLES[command](message, content)

    async def __add_to_whitelist(self, message: Message, content: List[str]) -> None:
        if len(content) < 1:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username provided for adding to whitelist.")
            return

        username = content[0]
        is_admin = bool(int(content[1])) if len(content) > 1 else False
        is_moderator = bool(int(content[2])) if len(content) > 2 else False

        if await DatabaseManager.is_user_moderator(message.from_user.username):
            if is_admin or is_moderator:
                await message.answer("❌ Moderator nie może nadawać statusu admina ani moderatora. ❌")
                await self._log_system_message(
                    logging.WARNING,
                    f"Moderator {message.from_user.username} attempted to assign admin or moderator status.",
                )
                return

        full_name = content[3] if len(content) > 3 else None
        email = content[4] if len(content) > 4 else None
        phone = content[5] if len(content) > 5 else None
        await DatabaseManager.add_user(username, is_admin, is_moderator, full_name, email, phone)
        await message.answer(get_user_added_message(username))
        await self._log_system_message(
            logging.INFO,
            f"User {username} added to whitelist by {message.from_user.username}.",
        )

    async def __remove_from_whitelist(self, message: Message, content: List[str]) -> None:
        if len(content) < 1:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username provided for removing from whitelist.")
            return

        username = content[0]
        await DatabaseManager.remove_user(username)
        await message.answer(get_user_removed_message(username))
        await self._log_system_message(
            logging.INFO,
            f"User {username} removed from whitelist by {message.from_user.username}.",
        )

    async def __update_whitelist(self, message: Message, content: List[str]) -> None:
        if len(content) < 1:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username provided for updating whitelist.")
            return

        username = content[0]
        is_admin = bool(int(content[1])) if len(content) > 1 else None
        is_moderator = bool(int(content[2])) if len(content) > 2 else None

        if await DatabaseManager.is_user_moderator(message.from_user.username):
            if is_admin or is_moderator:
                await message.answer("❌ Moderator nie może nadawać statusu admina ani moderatora.❌")
                await self._log_system_message(
                    logging.WARNING,
                    f"Moderator {message.from_user.username} attempted to assign admin or moderator status.",
                )
                return

        full_name = content[3] if len(content) > 3 else None
        email = content[4] if len(content) > 4 else None
        phone = content[5] if len(content) > 5 else None
        await DatabaseManager.update_user(username, is_admin, is_moderator, full_name, email, phone)
        await message.answer(get_user_updated_message(username))
        await self._log_system_message(logging.INFO, f"User {username} updated by {message.from_user.username}.")

    async def __list_whitelist(self, message: Message, _: List[str]) -> None:
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

    async def __list_admins(self, message: Message, _: List[str]) -> None:
        users = await DatabaseManager.get_admin_users()
        if not users:
            await message.answer(get_no_admins_found_message())
            await self._log_system_message(logging.INFO, "No admins found.")
            return

        response = "📃 Lista adminów:\n"
        response += self.__get_users_string(users)

        await message.answer(response)
        await self._log_system_message(logging.INFO, "Admin list sent to user.")

    async def __list_moderators(self, message: Message, _: List[str]) -> None:
        users = await DatabaseManager.get_moderator_users()
        if not users:
            await message.answer(get_no_moderators_found_message())
            await self._log_system_message(logging.INFO, "No moderators found.")
            return

        response = "📃 Lista moderatorów 📃\n"
        response += self.__get_users_string(users)

        await message.answer(response)
        await self._log_system_message(logging.INFO, "Moderator list sent to user.")

    async def __add_subscription_command(self, message: Message, content: List[str]) -> None:
        if len(content) < 2:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username or days provided for adding subscription.")
            return

        username = content[0]
        days = int(content[1])

        new_end_date = await DatabaseManager.add_subscription(username, days)
        await message.answer(get_subscription_extended_message(username, new_end_date))
        await self._log_system_message(
            logging.INFO,
            f"Subscription for user {username} extended by {message.from_user.username}.",
        )

    async def __remove_subscription_command(self, message: Message, content: List[str]) -> None:
        if len(content) < 1:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username provided for removing subscription.")
            return

        username = content[0]

        await DatabaseManager.remove_subscription(username)
        await message.answer(get_subscription_removed_message(username))
        await self._log_system_message(
            logging.INFO,
            f"Subscription for user {username} removed by {message.from_user.username}.",
        )

    async def __handle_transcription_request(self, message: Message, content: List[str]) -> None:
        if len(content) < 1:
            await message.answer(get_no_quote_provided_message())
            await self._log_system_message(logging.INFO, "No quote provided for transcription search.")
            return

        quote = ' '.join(content)
        await DatabaseManager.log_user_activity(message.from_user.username, f"/transkrypcja {quote}")

        search_transcriptions = SearchTranscriptions()
        context_size = 15
        result = await search_transcriptions.find_segment_with_context(quote, context_size)

        if not result:
            await message.answer(get_no_segments_found_message(quote))
            await self._log_system_message(logging.INFO, f"No segments found for quote: '{quote}'")
            return

        context_segments = result['context']
        response = get_transcription_response(quote, context_segments)
        await message.answer(response, parse_mode='Markdown')
        await self._log_system_message(
            logging.INFO,
            f"Transcription for quote '{quote}' sent to user '{message.from_user.username}'.",
        )

    def __get_users_string(self, users: List[asyncpg.Record]) -> str:
        return "\n".join([self.__format_user(user) for user in users]) + "\n"

    @staticmethod
    def __format_user(user: asyncpg.Record) -> str:
        return f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 Phone: {user['phone']}"
