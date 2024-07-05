import logging

from aiogram import (
    Dispatcher,
    Router,
    types,
)
from aiogram.filters import Command
from tabulate import tabulate

from bot.utils.database import DatabaseManager
from bot.utils.transcription_search import SearchTranscriptions

logger = logging.getLogger(__name__)
router = Router()

# Middleware
from bot.middlewares.auth_middleware import AuthorizationMiddleware
from bot.middlewares.error_middleware import ErrorHandlerMiddleware


# Definicja UserManager dla łatwiejszego dostępu do funkcji zarządzania użytkownikami
class UserManager:
    @staticmethod
    async def add_user(username, is_admin=False, is_moderator=False, full_name=None, email=None, phone=None, subscription_days=None):
        await DatabaseManager.add_user(username, is_admin, is_moderator, full_name, email, phone, subscription_days)

    @staticmethod
    async def remove_user(username):
        await DatabaseManager.remove_user(username)

    @staticmethod
    async def update_user(username, is_admin=None, is_moderator=None, full_name=None, email=None, phone=None, subscription_end=None):
        await DatabaseManager.update_user(username, is_admin, is_moderator, full_name, email, phone, subscription_end)

    @staticmethod
    async def get_all_users():
        return await DatabaseManager.get_all_users()

    @staticmethod
    async def get_admin_users():
        return await DatabaseManager.get_admin_users()

    @staticmethod
    async def get_moderator_users():
        return await DatabaseManager.get_moderator_users()

    @staticmethod
    async def add_subscription(username, days):
        return await DatabaseManager.add_subscription(username, days)

    @staticmethod
    async def remove_subscription(username):
        await DatabaseManager.remove_subscription(username)

    @staticmethod
    async def is_user_admin(username):
        return await DatabaseManager.is_user_admin(username)

    @staticmethod
    async def is_user_moderator(username):
        return await DatabaseManager.is_user_moderator(username)


@router.message(Command('admin'))
async def admin_help(message: types.Message):
    if not await UserManager.is_user_admin(message.from_user.username) and not await UserManager.is_user_moderator(
            message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.❌")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    help_message = """```🛠Instrukcje_dla_admina🛠

═════════════════════════════════
🔐 Zarządzanie użytkownikami: 🔐
═════════════════════════════════
➕ /addwhitelist <username> [is_admin=0] [is_moderator=0] [full_name] [email] [phone] - Dodaje użytkownika do whitelisty. Przykład: /addwhitelist johndoe 1 0 John Doe johndoe@example.com 123456789
➖ /removewhitelist <username> - Usuwa użytkownika z whitelisty. Przykład: /removewhitelist johndoe
✏️ /updatewhitelist <username> [is_admin] [is_moderator] [full_name] [email] [phone] - Aktualizuje dane użytkownika w whiteliście. Przykład: /updatewhitelist johndoe 0 1 John Doe johndoe@example.com 987654321
📃 /listwhitelist - Wyświetla listę wszystkich użytkowników w whiteliście.
📃 /listadmins - Wyświetla listę wszystkich adminów.
📃 /listmoderators - Wyświetla listę wszystkich moderatorów.

═════════════════════════════════
💳 Zarządzanie subskrypcjami: 💳
═════════════════════════════════
➕ /addsubscription <username> <days> - Dodaje subskrypcję użytkownikowi na określoną liczbę dni. Przykład: /addsubscription johndoe 30
🚫 /removesubscription <username> - Usuwa subskrypcję użytkownika. Przykład: /removesubscription johndoe

══════════════════════════════════
🔍 Zarządzanie transkrypcjami: 🔍
══════════════════════════════════
🔍 /transkrypcja <cytat> - Wyszukuje cytat w transkrypcjach i zwraca kontekst. Przykład: /transkrypcja Nie szkoda panu tego pięknego gabinetu?

```"""
    await message.answer(help_message, parse_mode='Markdown')
    logger.info("Admin help message sent to user.")
    await DatabaseManager.log_system_message("INFO", f"Admin help message sent to user '{message.from_user.username}'.")


@router.message(Command(commands=['addwhitelist', 'addw']))
async def add_to_whitelist(message: types.Message):
    if not await UserManager.is_user_admin(message.from_user.username) and not await UserManager.is_user_moderator(
            message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.❌")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("✏️ Podaj nazwę użytkownika do dodania.✏️")
        logger.info("No username provided for adding to whitelist.")
        await DatabaseManager.log_system_message("INFO", "No username provided for adding to whitelist.")
        return

    username = params[0]
    is_admin = bool(int(params[1])) if len(params) > 1 else False
    is_moderator = bool(int(params[2])) if len(params) > 2 else False

    if await UserManager.is_user_moderator(message.from_user.username):
        if is_admin or is_moderator:
            await message.answer("❌ Moderator nie może nadawać statusu admina ani moderatora. ❌")
            logger.warning(f"Moderator {message.from_user.username} attempted to assign admin or moderator status.")
            await DatabaseManager.log_system_message("WARNING",
                                                     f"Moderator {message.from_user.username} attempted to assign admin or moderator status.")
            return

    full_name = params[3] if len(params) > 3 else None
    email = params[4] if len(params) > 4 else None
    phone = params[5] if len(params) > 5 else None
    await UserManager.add_user(username, is_admin, is_moderator, full_name, email, phone)
    await message.answer(f"✅ Dodano {username} do whitelisty.✅")
    logger.info(f"User {username} added to whitelist by {message.from_user.username}.")
    await DatabaseManager.log_system_message("INFO", f"User {username} added to whitelist by {message.from_user.username}'.")


@router.message(Command(commands=['removewhitelist', 'removew']))
async def remove_from_whitelist(message: types.Message):
    if not await UserManager.is_user_admin(message.from_user.username) and not await UserManager.is_user_moderator(
            message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.❌")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("✏️ Podaj nazwę użytkownika do usunięcia.✏️")
        logger.info("No username provided for removing from whitelist.")
        await DatabaseManager.log_system_message("INFO", "No username provided for removing from whitelist.")
        return

    username = params[0]
    await UserManager.remove_user(username)
    await message.answer(f"✅ Usunięto {username} z whitelisty.✅")
    logger.info(f"User {username} removed from whitelist by {message.from_user.username}.")
    await DatabaseManager.log_system_message("INFO", f"User {username} removed from whitelist by {message.from_user.username}'.")


@router.message(Command(commands=['updatewhitelist', 'updatew']))
async def update_whitelist(message: types.Message):
    if not await UserManager.is_user_admin(message.from_user.username) and not await UserManager.is_user_moderator(
            message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.❌")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("✏️ Podaj nazwę użytkownika do zaktualizowania.✏️")
        logger.info("No username provided for updating whitelist.")
        await DatabaseManager.log_system_message("INFO", "No username provided for updating whitelist.")
        return

    username = params[0]
    is_admin = bool(int(params[1])) if len(params) > 1 else None
    is_moderator = bool(int(params[2])) if len(params) > 2 else None

    if await UserManager.is_user_moderator(message.from_user.username):
        if is_admin or is_moderator:
            await message.answer("❌ Moderator nie może nadawać statusu admina ani moderatora.❌")
            logger.warning(f"Moderator {message.from_user.username} attempted to assign admin or moderator status.")
            await DatabaseManager.log_system_message("WARNING",
                                                     f"Moderator {message.from_user.username} attempted to assign admin or moderator status.")
            return

    full_name = params[3] if len(params) > 3 else None
    email = params[4] if len(params) > 4 else None
    phone = params[5] if len(params) > 5 else None
    await UserManager.update_user(username, is_admin, is_moderator, full_name, email, phone)
    await message.answer(f"✅ Zaktualizowano dane użytkownika {username}.✅")
    logger.info(f"User {username} updated by {message.from_user.username}.")
    await DatabaseManager.log_system_message("INFO", f"User {username} updated by {message.from_user.username}'.")


@router.message(Command(commands=['listwhitelist', 'listw']))
async def list_whitelist(message: types.Message):
    if not await UserManager.is_user_admin(message.from_user.username) and not await UserManager.is_user_moderator(
            message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.❌")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    users = await UserManager.get_all_users()
    if not users:
        await message.answer("📭 Whitelist jest pusta.📭")
        logger.info("Whitelist is empty.")
        await DatabaseManager.log_system_message("INFO", "Whitelist is empty.")
        return

    table = [["Username", "Full Name", "Email", "Phone", "Subskrypcja do"]]
    for user in users:
        table.append([user['username'], user['full_name'], user['email'], user['phone'], user['subscription_end']])

    response = f"```whitelista\n{tabulate(table, headers='firstrow', tablefmt='grid')}```"
    await message.answer(response, parse_mode='Markdown')
    logger.info("Whitelist sent to user.")
    await DatabaseManager.log_system_message("INFO", "Whitelist sent to user.")


@router.message(Command(commands=['listadmins', 'listad']))
async def list_admins(message: types.Message):
    if not await UserManager.is_user_admin(message.from_user.username) and not await UserManager.is_user_moderator(
            message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.❌")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    users = await UserManager.get_admin_users()
    if not users:
        await message.answer("📭 Nie znaleziono adminów.📭")
        logger.info("No admins found.")
        await DatabaseManager.log_system_message("INFO", "No admins found.")
        return

    response = "📃 Lista adminów:\n"
    for user in users:
        response += f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 Phone: {user['phone']}\n"

    await message.answer(response)
    logger.info("Admin list sent to user.")
    await DatabaseManager.log_system_message("INFO", "Admin list sent to user.")


@router.message(Command(commands=['listmoderators', 'listmod']))
async def list_moderators(message: types.Message):
    if not await UserManager.is_user_admin(message.from_user.username) and not await UserManager.is_user_moderator(
            message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.❌")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    users = await UserManager.get_moderator_users()
    if not users:
        await message.answer("📭 Nie znaleziono moderatorów.📭")
        logger.info("No moderators found.")
        await DatabaseManager.log_system_message("INFO", "No moderators found.")
        return

    response = "📃 Lista moderatorów 📃\n"
    for user in users:
        response += f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 Phone: {user['phone']}\n"

    await message.answer(response)
    logger.info("Moderator list sent to user.")
    await DatabaseManager.log_system_message("INFO", "Moderator list sent to user.")


@router.message(Command(commands=['addsubscription', 'addsub']))
async def add_subscription_command(message: types.Message):
    if not await UserManager.is_user_admin(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania subskrypcjami.❌ ")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    params = message.text.split()[1:]
    if len(params) < 2:
        await message.answer("✏️ Podaj nazwę użytkownika i liczbę dni subskrypcji.✏️")
        logger.info("No username or days provided for adding subscription.")
        await DatabaseManager.log_system_message("INFO", "No username or days provided for adding subscription.")
        return

    username = params[0]
    days = int(params[1])

    new_end_date = await UserManager.add_subscription(username, days)
    await message.answer(f"✅ Subskrypcja dla użytkownika {username} przedłużona do {new_end_date}.✅")
    logger.info(f"Subscription for user {username} extended by {message.from_user.username}.")
    await DatabaseManager.log_system_message("INFO", f"Subscription for user {username} extended by {message.from_user.username}'.")


@router.message(Command(commands=['removesubscription', 'removesub']))
async def remove_subscription_command(message: types.Message):
    if not await UserManager.is_user_admin(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania subskrypcjami.❌")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("✏️ Podaj nazwę użytkownika, aby usunąć jego subskrypcję.✏️")
        logger.info("No username provided for removing subscription.")
        await DatabaseManager.log_system_message("INFO", "No username provided for removing subscription.")
        return

    username = params[0]

    await UserManager.remove_subscription(username)
    await message.answer(f"✅ Subskrypcja dla użytkownika {username} została usunięta.✅")
    logger.info(f"Subscription for user {username} removed by {message.from_user.username}.")
    await DatabaseManager.log_system_message("INFO", f"Subscription for user {username} removed by {message.from_user.username}'.")


@router.message(Command(commands=['transkrypcja', 'trans']))
async def handle_transcription_request(message: types.Message):
    if not await UserManager.is_user_admin(message.from_user.username) and not await UserManager.is_user_moderator(
            message.from_user.username,
    ):
        await message.answer("❌ Nie masz uprawnień do używania tej komendy.❌")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        await DatabaseManager.log_system_message("WARNING", f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    content = message.text.split()
    if len(content) < 2:
        await message.answer("✏️ Podaj cytat, który chcesz znaleźć.✏️")
        logger.info("No quote provided for transcription search.")
        await DatabaseManager.log_system_message("INFO", "No quote provided for transcription search.")
        return

    quote = ' '.join(content[1:])
    logger.info(f"Searching transcription for quote: '{quote}'")
    await DatabaseManager.log_user_activity(message.from_user.username, f"/transkrypcja {quote}")

    search_transcriptions = SearchTranscriptions(router)
    context_size = 15
    result = await search_transcriptions.find_segment_with_context(quote, context_size)

    if not result:
        await message.answer("❌ Nie znaleziono pasujących segmentów.❌")
        logger.info(f"No segments found for quote: '{quote}'")
        await DatabaseManager.log_system_message("INFO", f"No segments found for quote: '{quote}'")
        return

    target_segment = result['target']
    context_segments = result['context']

    response = f"🔍 Transkrypcja dla cytatu: \"{quote}\"\n\n```\n"
    for segment in context_segments:
        response += f"🆔 {segment['id']} - {segment['text']}\n"
    response += "```"

    await message.answer(response, parse_mode='Markdown')
    logger.info(f"Transcription for quote '{quote}' sent to user '{message.from_user.username}'.")
    await DatabaseManager.log_system_message("INFO", f"Transcription for quote '{quote}' sent to user '{message.from_user.username}'.")


def register_admin_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)


# Ustawienie middleware'ów
router.message.middleware(AuthorizationMiddleware())
router.message.middleware(ErrorHandlerMiddleware())
