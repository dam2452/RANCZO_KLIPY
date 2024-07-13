#fixme to jest całe chujowe przerośniete ale nwm jak to najmądrzej zrobić to narazie tylko przejabałem przez gpt oryginał żeby pod schmemat było żeby ci się odrobine lepiej czytało
#fixme jak tak patrze to prawie całe do bana ale nie dłubie tego narazie bo to trzeba wgl lepiej zrobić
from datetime import date
import logging
from typing import (
    List,
    Optional,
)

from aiogram import types
import asyncpg
from tabulate import tabulate

from bot.handlers.bot_message_handler import BotMessageHandler
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


class UserManager:
    @staticmethod
    async def add_user(
            username: str, is_admin: Optional[bool] = False, is_moderator: Optional[bool] = False,
            full_name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None,
            subscription_days: Optional[int] = None,
    ) -> None:
        await DatabaseManager.add_user(username, is_admin, is_moderator, full_name, email, phone, subscription_days)

    @staticmethod
    async def remove_user(username: str) -> None:
        await DatabaseManager.remove_user(username)

    @staticmethod
    async def update_user(
            username: str, is_admin: Optional[bool] = False, is_moderator: Optional[bool] = False,
            full_name: Optional[str] = None, email: Optional[str] = None, phone: Optional[str] = None,
            subscription_end: Optional[int] = None,
    ) -> None:
        await DatabaseManager.update_user(username, is_admin, is_moderator, full_name, email, phone, subscription_end)

    @staticmethod
    async def get_all_users() -> Optional[List[asyncpg.Record]]:
        return await DatabaseManager.get_all_users()

    @staticmethod
    async def get_admin_users() -> Optional[List[asyncpg.Record]]:
        return await DatabaseManager.get_admin_users()

    @staticmethod
    async def get_moderator_users() -> Optional[List[asyncpg.Record]]:
        return await DatabaseManager.get_moderator_users()

    @staticmethod
    async def add_subscription(username: str, days: int) -> Optional[date]:
        return await DatabaseManager.add_subscription(username, days)

    @staticmethod
    async def remove_subscription(username: str) -> None:
        await DatabaseManager.remove_subscription(username)

    @staticmethod
    async def is_user_admin(username: str) -> Optional[bool]:
        return await DatabaseManager.is_user_admin(username)

    @staticmethod
    async def is_user_moderator(username: str) -> Optional[bool]:
        return await DatabaseManager.is_user_moderator(username)


class AdminCommandHandler(BotMessageHandler):
    def get_commands(self) -> List[str]:
        return [
            'admin', 'addwhitelist', 'removewhitelist', 'updatewhitelist',
            'listwhitelist', 'listadmins', 'listmoderators', 'addsubscription',
            'removesubscription', 'transkrypcja',
        ]

    async def _do_handle(self, message: types.Message) -> None:
        username = message.from_user.username
        if not await UserManager.is_user_admin(username) and not await UserManager.is_user_moderator(username):
            await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.❌")
            await self._log_system_message(logging.WARNING, f"Unauthorized access attempt by user: {username}")
            return

        command = message.get_command(pure=True)
        content = message.text.split()[1:]

        if command == 'admin':
            await message.answer(get_admin_help_message(), parse_mode='Markdown')
        elif command in {'addwhitelist', 'addw'}:
            await self._add_to_whitelist(message, content)
        elif command in {'removewhitelist', 'removew'}:
            await self._remove_from_whitelist(message, content)
        elif command in {'updatewhitelist', 'updatew'}:
            await self._update_whitelist(message, content)
        elif command in {'listwhitelist', 'listw'}:
            await self._list_whitelist(message)
        elif command in {'listadmins', 'listad'}:
            await self._list_admins(message)
        elif command in {'listmoderators', 'listmod'}:
            await self._list_moderators(message)
        elif command in {'addsubscription', 'addsub'}:
            await self._add_subscription_command(message, content)
        elif command in {'removesubscription', 'removesub'}:
            await self._remove_subscription_command(message, content)
        elif command in {'transkrypcja', 'trans'}:
            await self._handle_transcription_request(message, content)

    async def _add_to_whitelist(self, message: types.Message, content: List[str]) -> None:
        if len(content) < 1:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username provided for adding to whitelist.")
            return

        username = content[0]
        is_admin = bool(int(content[1])) if len(content) > 1 else False
        is_moderator = bool(int(content[2])) if len(content) > 2 else False

        if await UserManager.is_user_moderator(message.from_user.username):
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
        await UserManager.add_user(username, is_admin, is_moderator, full_name, email, phone)
        await message.answer(get_user_added_message(username))
        await self._log_system_message(
            logging.INFO,
            f"User {username} added to whitelist by {message.from_user.username}.",
        )

    async def _remove_from_whitelist(self, message: types.Message, content: List[str]) -> None:
        if len(content) < 1:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username provided for removing from whitelist.")
            return

        username = content[0]
        await UserManager.remove_user(username)
        await message.answer(get_user_removed_message(username))
        await self._log_system_message(
            logging.INFO,
            f"User {username} removed from whitelist by {message.from_user.username}.",
        )

    async def _update_whitelist(self, message: types.Message, content: List[str]) -> None:
        if len(content) < 1:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username provided for updating whitelist.")
            return

        username = content[0]
        is_admin = bool(int(content[1])) if len(content) > 1 else None
        is_moderator = bool(int(content[2])) if len(content) > 2 else None

        if await UserManager.is_user_moderator(message.from_user.username):
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
        await UserManager.update_user(username, is_admin, is_moderator, full_name, email, phone)
        await message.answer(get_user_updated_message(username))
        await self._log_system_message(logging.INFO, f"User {username} updated by {message.from_user.username}.")

    async def _list_whitelist(self, message: types.Message) -> None:
        users = await UserManager.get_all_users()
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

    async def _list_admins(self, message: types.Message) -> None:
        users = await UserManager.get_admin_users()
        if not users:
            await message.answer(get_no_admins_found_message())
            await self._log_system_message(logging.INFO, "No admins found.")
            return

        response = "📃 Lista adminów:\n"
        response += self._get_users_string(users)

        await message.answer(response)
        await self._log_system_message(logging.INFO, "Admin list sent to user.")

    async def _list_moderators(self, message: types.Message) -> None:
        users = await UserManager.get_moderator_users()
        if not users:
            await message.answer(get_no_moderators_found_message())
            await self._log_system_message(logging.INFO, "No moderators found.")
            return

        response = "📃 Lista moderatorów 📃\n"
        response += self._get_users_string(users)

        await message.answer(response)
        await self._log_system_message(logging.INFO, "Moderator list sent to user.")

    async def _add_subscription_command(self, message: types.Message, content: List[str]) -> None:
        if len(content) < 2:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username or days provided for adding subscription.")
            return

        username = content[0]
        days = int(content[1])

        new_end_date = await UserManager.add_subscription(username, days)
        await message.answer(get_subscription_extended_message(username, new_end_date))
        await self._log_system_message(
            logging.INFO,
            f"Subscription for user {username} extended by {message.from_user.username}.",
        )

    async def _remove_subscription_command(self, message: types.Message, content: List[str]) -> None:
        if len(content) < 1:
            await message.answer(get_no_username_provided_message())
            await self._log_system_message(logging.INFO, "No username provided for removing subscription.")
            return

        username = content[0]

        await UserManager.remove_subscription(username)
        await message.answer(get_subscription_removed_message(username))
        await self._log_system_message(
            logging.INFO,
            f"Subscription for user {username} removed by {message.from_user.username}.",
        )

    async def _handle_transcription_request(self, message: types.Message, content: List[str]) -> None:
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

    def _get_users_string(self, users: List[asyncpg.Record]) -> str:
        return "\n".join([self._format_user(user) for user in users]) + "\n"

    @staticmethod
    def _format_user(user: asyncpg.Record) -> str:
        return f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 Phone: {user['phone']}"
