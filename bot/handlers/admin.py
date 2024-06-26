import logging
from aiogram import Router, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from bot.utils.db import add_user, remove_user, update_user, is_user_admin, is_user_moderator, get_all_users, get_admin_users, get_moderator_users, add_subscription, remove_subscription

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command('admin'))
async def admin_help(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("Nie masz uprawnień do zarządzania whitelistą.")
        return

    help_message = """
🛠 *Instrukcje dla admina* 🛠

Komendy do zarządzania whitelistą:

➕ `/addwhitelist <username> [is_admin=0] [is_moderator=0] [full_name] [email] [phone]`
Dodaje użytkownika do whitelisty.
Przykład: `/addwhitelist johndoe 1 0 John Doe johndoe@example.com 123456789`

➖ `/removewhitelist <username>`
Usuwa użytkownika z whitelisty.
Przykład: `/removewhitelist johndoe`

✏️ `/updatewhitelist <username> [is_admin] [is_moderator] [full_name] [email] [phone]`
Aktualizuje dane użytkownika w whiteliście.
Przykład: `/updatewhitelist johndoe 0 1 John Doe johndoe@example.com 987654321`

📃 `/listwhitelist`
Wyświetla listę wszystkich użytkowników w whiteliście.

📃 `/listadmins`
Wyświetla listę wszystkich adminów.

📃 `/listmoderators`
Wyświetla listę wszystkich moderatorów.

💳 `/addsubscription <username> <days>`
Dodaje subskrypcję użytkownikowi na określoną liczbę dni.
Przykład: `/addsubscription johndoe 30`

🚫 `/removesubscription <username>`
Usuwa subskrypcję użytkownika.
Przykład: `/removesubscription johndoe`
"""
    await message.answer(help_message, parse_mode='Markdown')

@router.message(Command('addwhitelist'))
async def add_to_whitelist(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("Nie masz uprawnień do zarządzania whitelistą.")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("Podaj nazwę użytkownika do dodania.")
        return

    username = params[0]
    is_admin = bool(int(params[1])) if len(params) > 1 else False
    is_moderator = bool(int(params[2])) if len(params) > 2 else False

    if await is_user_moderator(message.from_user.username):
        if is_admin or is_moderator:
            await message.answer("Moderator nie może nadawać statusu admina ani moderatora.")
            return

    full_name = params[3] if len(params) > 3 else None
    email = params[4] if len(params) > 4 else None
    phone = params[5] if len(params) > 5 else None
    await add_user(username, is_admin, is_moderator, full_name, email, phone)
    await message.answer(f"Dodano {username} do whitelisty.")

@router.message(Command('removewhitelist'))
async def remove_from_whitelist(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("Nie masz uprawnień do zarządzania whitelistą.")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("Podaj nazwę użytkownika do usunięcia.")
        return

    username = params[0]
    await remove_user(username)
    await message.answer(f"Usunięto {username} z whitelisty.")

@router.message(Command('updatewhitelist'))
async def update_whitelist(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("Nie masz uprawnień do zarządzania whitelistą.")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("Podaj nazwę użytkownika do zaktualizowania.")
        return

    username = params[0]
    is_admin = bool(int(params[1])) if len(params) > 1 else None
    is_moderator = bool(int(params[2])) if len(params) > 2 else None

    if await is_user_moderator(message.from_user.username):
        if is_admin or is_moderator:
            await message.answer("Moderator nie może nadawać statusu admina ani moderatora.")
            return

    full_name = params[3] if len(params) > 3 else None
    email = params[4] if len(params) > 4 else None
    phone = params[5] if len(params) > 5 else None
    await update_user(username, is_admin, is_moderator, full_name, email, phone)
    await message.answer(f"Zaktualizowano dane użytkownika {username}.")

@router.message(Command('listwhitelist'))
async def list_whitelist(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("Nie masz uprawnień do zarządzania whitelistą.")
        return

    users = await get_all_users()
    if not users:
        await message.answer("Whitelist jest pusta.")
        return

    response = "Lista użytkowników w whiteliście:\n"
    for user in users:
        response += f"Username: {user['username']}, Full Name: {user['full_name']}, Email: {user['email']}, Phone: {user['phone']}, Subskrypcja do: {user['subscription_end']}\n"

    await message.answer(response)

@router.message(Command('listadmins'))
async def list_admins(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("Nie masz uprawnień do zarządzania whitelistą.")
        return

    users = await get_admin_users()
    if not users:
        await message.answer("Nie znaleziono adminów.")
        return

    response = "Lista adminów:\n"
    for user in users:
        response += f"Username: {user['username']}, Full Name: {user['full_name']}, Email: {user['email']}, Phone: {user['phone']}\n"

    await message.answer(response)

@router.message(Command('listmoderators'))
async def list_moderators(message: Message):
    if not await is_user_admin(message.from_user.username) and not await is_user_moderator(message.from_user.username):
        await message.answer("Nie masz uprawnień do zarządzania whitelistą.")
        return

    users = await get_moderator_users()
    if not users:
        await message.answer("Nie znaleziono moderatorów.")
        return

    response = "Lista moderatorów:\n"
    for user in users:
        response += f"Username: {user['username']}, Full Name: {user['full_name']}, Email: {user['email']}, Phone: {user['phone']}\n"

    await message.answer(response)

@router.message(Command('addsubscription'))
async def add_subscription_command(message: Message):
    if not await is_user_admin(message.from_user.username):
        await message.answer("Nie masz uprawnień do zarządzania subskrypcjami.")
        return

    params = message.text.split()[1:]
    if len(params) < 2:
        await message.answer("Podaj nazwę użytkownika i liczbę dni subskrypcji.")
        return

    username = params[0]
    days = int(params[1])

    new_end_date = await add_subscription(username, days)
    await message.answer(f"Subskrypcja dla użytkownika {username} przedłużona do {new_end_date}.")

@router.message(Command('removesubscription'))
async def remove_subscription_command(message: Message):
    if not await is_user_admin(message.from_user.username):
        await message.answer("Nie masz uprawnień do zarządzania subskrypcjami.")
        return

    params = message.text.split()[1:]
    if len(params) < 1:
        await message.answer("Podaj nazwę użytkownika, aby usunąć jego subskrypcję.")
        return

    username = params[0]

    await remove_subscription(username)
    await message.answer(f"Subskrypcja dla użytkownika {username} została usunięta.")

def register_admin_handlers(dispatcher: Dispatcher):
    dispatcher.include_router(router)
