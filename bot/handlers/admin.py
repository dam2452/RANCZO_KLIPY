from telebot import TeleBot
from ..utils.db import add_user, remove_user, update_user, is_user_admin, is_user_moderator, get_all_users, \
    get_admin_users, get_moderator_users


def register_admin_handlers(bot: TeleBot):
    @bot.message_handler(commands=['addwhitelist', 'removewhitelist', 'updatewhitelist'])
    def manage_whitelist(message):
        if not is_user_admin(message.from_user.username) and not is_user_moderator(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do zarządzania whitelistą.")
            return

        command, *params = message.text.split()
        if command == '/addwhitelist':
            if len(params) < 1:
                bot.reply_to(message, "Podaj nazwę użytkownika do dodania.")
                return
            username = params[0]
            is_admin = int(params[1]) if len(params) > 1 else 0
            is_moderator = int(params[2]) if len(params) > 2 else 0

            if is_user_moderator(message.from_user.username):
                if is_admin or is_moderator:
                    bot.reply_to(message, "Moderator nie może nadawać statusu admina ani moderatora.")
                    return

            full_name = params[3] if len(params) > 3 else None
            email = params[4] if len(params) > 4 else None
            phone = params[5] if len(params) > 5 else None
            add_user(username, is_admin, is_moderator, full_name, email, phone)
            bot.reply_to(message, f"Dodano {username} do whitelisty.")

        elif command == '/removewhitelist':
            if len(params) < 1:
                bot.reply_to(message, "Podaj nazwę użytkownika do usunięcia.")
                return
            username = params[0]
            remove_user(username)
            bot.reply_to(message, f"Usunięto {username} z whitelisty.")

        elif command == '/updatewhitelist':
            if len(params) < 1:
                bot.reply_to(message, "Podaj nazwę użytkownika do zaktualizowania.")
                return
            username = params[0]
            is_admin = int(params[1]) if len(params) > 1 else None
            is_moderator = int(params[2]) if len(params) > 2 else None

            if is_user_moderator(message.from_user.username):
                if is_admin or is_moderator:
                    bot.reply_to(message, "Moderator nie może nadawać statusu admina ani moderatora.")
                    return

            full_name = params[3] if len(params) > 3 else None
            email = params[4] if len(params) > 4 else None
            phone = params[5] if len(params) > 5 else None
            update_user(username, is_admin, is_moderator, full_name, email, phone)
            bot.reply_to(message, f"Zaktualizowano dane użytkownika {username}.")

    @bot.message_handler(commands=['listwhitelist'])
    def list_whitelist(message):
        if not is_user_admin(message.from_user.username) and not is_user_moderator(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do zarządzania whitelistą.")
            return

        users = get_all_users()
        if not users:
            bot.reply_to(message, "Whitelist jest pusta.")
            return

        response = "Lista użytkowników w whiteliście:\n"
        for user in users:
            response += f"Username: {user[0]}, Full Name: {user[3]}, Email: {user[4]}, Phone: {user[5]}\n"

        bot.reply_to(message, response)

    @bot.message_handler(commands=['listadmins'])
    def list_admins(message):
        if not is_user_admin(message.from_user.username) and not is_user_moderator(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do zarządzania whitelistą.")
            return

        users = get_admin_users()
        if not users:
            bot.reply_to(message, "Nie znaleziono adminów.")
            return

        response = "Lista adminów:\n"
        for user in users:
            response += f"Username: {user[0]}, Full Name: {user[1]}, Email: {user[2]}, Phone: {user[3]}\n"

        bot.reply_to(message, response)

    @bot.message_handler(commands=['listmoderators'])
    def list_moderators(message):
        if not is_user_admin(message.from_user.username) and not is_user_moderator(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do zarządzania whitelistą.")
            return

        users = get_moderator_users()
        if not users:
            bot.reply_to(message, "Nie znaleziono moderatorów.")
            return

        response = "Lista moderatorów:\n"
        for user in users:
            response += f"Username: {user[0]}, Full Name: {user[1]}, Email: {user[2]}, Phone: {user[3]}\n"

        bot.reply_to(message, response)

    @bot.message_handler(commands=['admin'])
    def admin_help(message):
        if not is_user_admin(message.from_user.username) and not is_user_moderator(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do zarządzania whitelistą.")
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
"""
        bot.reply_to(message, help_message, parse_mode='Markdown')
