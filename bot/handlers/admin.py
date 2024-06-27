import logging
from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from bot.utils.db import add_user, remove_user, update_user, is_user_admin, is_user_moderator, get_all_users, get_admin_users, get_moderator_users, add_subscription, remove_subscription
from bot.search_transcriptions import find_segment_with_context
import logging
from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from bot.utils.db import add_user, remove_user, update_user, is_user_admin, is_user_moderator, get_all_users, get_admin_users, get_moderator_users, add_subscription, remove_subscription
from bot.search_transcriptions import find_segment_with_context
from tabulate import tabulate

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('admin'))
async def admin_help(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    help_message = """```🛠Instrukcje_dla_admina🛠

    ╔ ═════════════════════════════════════╗
    ║       🔐 Zarządzanie użytkownikami:  ║
    ╚ ═════════════════════════════════════╝
➕ /addwhitelist <username> [is_admin=0] [is_moderator=0] [full_name] [email] [phone] - Dodaje użytkownika do whitelisty. Przykład: /addwhitelist johndoe 1 0 John Doe johndoe@example.com 123456789
➖ /removewhitelist <username> - Usuwa użytkownika z whitelisty. Przykład: /removewhitelist johndoe
✏️ /updatewhitelist <username> [is_admin] [is_moderator] [full_name] [email] [phone] - Aktualizuje dane użytkownika w whiteliście. Przykład: /updatewhitelist johndoe 0 1 John Doe johndoe@example.com 987654321
📃 /listwhitelist - Wyświetla listę wszystkich użytkowników w whiteliście.
📃 /listadmins - Wyświetla listę wszystkich adminów.
📃 /listmoderators - Wyświetla listę wszystkich moderatorów.

    ╔ ═════════════════════════════════════╗
    ║     💳 Zarządzanie subskrypcjami:    ║
    ╚ ═════════════════════════════════════╝
➕ /addsubscription <username> <days> - Dodaje subskrypcję użytkownikowi na określoną liczbę dni. Przykład: /addsubscription johndoe 30
🚫 /removesubscription <username> - Usuwa subskrypcję użytkownika. Przykład: /removesubscription johndoe


    ╔ ═════════════════════════════════════╗
    ║     🔍 Zarządzanie transkrypcjami:   ║
    ╚ ═════════════════════════════════════╝
🔍 /transkrypcja <cytat> - Wyszukuje cytat w transkrypcjach i zwraca kontekst. Przykład: /transkrypcja Nie szkoda panu tego pięknego gabinetu?


```"""
    await message.answer(help_message, parse_mode='Markdown')
    logger.info("Admin help message sent to user.")


@router.message(Command('addwhitelist'))
async def add_to_whitelist(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("✏️ Podaj nazwę użytkownika do dodania.")
        logger.info("No username provided for adding to whitelist.")
        return

    username = params[0]
    is_admin = bool(int(params[1])) if len(params) > 1 else False
    is_moderator = bool(int(params[2])) if len(params) > 2 else False

    if await is_user_moderator(message.from_user.username):
        if is_admin or is_moderator:
            await message.answer("❌ Moderator nie może nadawać statusu admina ani moderatora.")
            logger.warning(f"Moderator {message.from_user.username} attempted to assign admin or moderator status.")
            return

    full_name = params[3] if len(params) > 3 else None
    email = params[4] if len(params) > 4 else None
    phone = params[5] if len(params) > 5 else None
    await add_user(username, is_admin, is_moderator, full_name, email, phone)
    await message.answer(f"✅ Dodano {username} do whitelisty.")
    logger.info(f"User {username} added to whitelist by {message.from_user.username}.")


@router.message(Command('removewhitelist'))
async def remove_from_whitelist(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("✏️ Podaj nazwę użytkownika do usunięcia.")
        logger.info("No username provided for removing from whitelist.")
        return

    username = params[0]
    await remove_user(username)
    await message.answer(f"✅ Usunięto {username} z whitelisty.")
    logger.info(f"User {username} removed from whitelist by {message.from_user.username}.")


@router.message(Command('updatewhitelist'))
async def update_whitelist(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("✏️ Podaj nazwę użytkownika do zaktualizowania.")
        logger.info("No username provided for updating whitelist.")
        return

    username = params[0]
    is_admin = bool(int(params[1])) if len(params) > 1 else None
    is_moderator = bool(int(params[2])) if len(params) > 2 else None

    if await is_user_moderator(message.from_user.username):
        if is_admin or is_moderator:
            await message.answer("❌ Moderator nie może nadawać statusu admina ani moderatora.")
            logger.warning(f"Moderator {message.from_user.username} attempted to assign admin or moderator status.")
            return

    full_name = params[3] if len(params) > 3 else None
    email = params[4] if len(params) > 4 else None
    phone = params[5] if len(params) > 5 else None
    await update_user(username, is_admin, is_moderator, full_name, email, phone)
    await message.answer(f"✅ Zaktualizowano dane użytkownika {username}.")
    logger.info(f"User {username} updated by {message.from_user.username}.")


@router.message(Command('listwhitelist'))
async def list_whitelist(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    users = await get_all_users()
    if not users:
        await message.answer("📭 Whitelist jest pusta.")
        logger.info("Whitelist is empty.")
        return

    table = [["Username", "Full Name", "Email", "Phone", "Subskrypcja do"]]
    for user in users:
        table.append([user['username'], user['full_name'], user['email'], user['phone'], user['subscription_end']])

    response = f"```whitelista\n{tabulate(table, headers='firstrow', tablefmt='grid')}```"
    await message.answer(response, parse_mode='Markdown')
    logger.info("Whitelist sent to user.")


@router.message(Command('listadmins'))
async def list_admins(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    users = await get_admin_users()
    if not users:
        await message.answer("📭 Nie znaleziono adminów.")
        logger.info("No admins found.")
        return

    response = "📃 Lista adminów:\n"
    for user in users:
        response += f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 Phone: {user['phone']}\n"

    await message.answer(response)
    logger.info("Admin list sent to user.")


@router.message(Command('listmoderators'))
async def list_moderators(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania whitelistą.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    users = await get_moderator_users()
    if not users:
        await message.answer("📭 Nie znaleziono moderatorów.")
        logger.info("No moderators found.")
        return

    response = "📃 Lista moderatorów:\n"
    for user in users:
        response += f"👤 Username: {user['username']}, 📛 Full Name: {user['full_name']}, ✉️ Email: {user['email']}, 📞 Phone: {user['phone']}\n"

    await message.answer(response)
    logger.info("Moderator list sent to user.")


@router.message(Command('addsubscription'))
async def add_subscription_command(message: Message):
    if not await is_user_admin(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania subskrypcjami.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    params = message.text.split()[1:]
    if len(params) < 2:
        await message.answer("✏️ Podaj nazwę użytkownika i liczbę dni subskrypcji.")
        logger.info("No username or days provided for adding subscription.")
        return

    username = params[0]
    days = int(params[1])

    new_end_date = await add_subscription(username, days)
    await message.answer(f"✅ Subskrypcja dla użytkownika {username} przedłużona do {new_end_date}.")
    logger.info(f"Subscription for user {username} extended by {message.from_user.username}.")


@router.message(Command('removesubscription'))
async def remove_subscription_command(message: Message):
    if not await is_user_admin(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do zarządzania subskrypcjami.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("✏️ Podaj nazwę użytkownika, aby usunąć jego subskrypcję.")
        logger.info("No username provided for removing subscription.")
        return

    username = params[0]

    await remove_subscription(username)
    await message.answer(f"✅ Subskrypcja dla użytkownika {username} została usunięta.")
    logger.info(f"Subscription for user {username} removed by {message.from_user.username}.")


@router.message(Command('transkrypcja'))
async def handle_transcription_request(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("❌ Nie masz uprawnień do używania tej komendy.")
        logger.warning(f"Unauthorized access attempt by user: {message.from_user.username}")
        return

    content = message.text.split()
    if len(content) < 2:
        await message.answer("✏️ Podaj cytat, który chcesz znaleźć.")
        logger.info("No quote provided for transcription search.")
        return

    quote = ' '.join(content[1:])
    logger.info(f"Searching transcription for quote: '{quote}'")

    context_size = 30
    result = await find_segment_with_context(quote, context_size)

    if not result:
        await message.answer("❌ Nie znaleziono pasujących segmentów.")
        logger.info(f"No segments found for quote: '{quote}'")
        return

    target_segment = result['target']
    context_segments = result['context']

    response = f"🔍 Transkrypcja dla cytatu: '{quote}'\n\n"
    for segment in context_segments:
        response += f"🆔 ID: {segment['id']} - {segment['text']}\n"

    await message.answer(response)
    logger.info(f"Transcription for quote '{quote}' sent to user '{message.from_user.username}'.")


def register_admin_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)