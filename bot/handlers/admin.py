from telebot import TeleBot
from ..utils.db import add_user, remove_user, update_user, is_user_admin, get_all_users


def register_admin_handlers(bot: TeleBot):
    @bot.message_handler(commands=['addwhitelist', 'removewhitelist', 'updatewhitelist'])
    def manage_whitelist(message):
        if not is_user_admin(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do zarządzania whitelistą.")
            return

        command, *params = message.text.split()
        if command == '/addwhitelist':
            if len(params) < 1:
                bot.reply_to(message, "Podaj nazwę użytkownika do dodania.")
                return
            username = params[0]
            is_admin = int(params[1]) if len(params) > 1 else 0
            is_vip = int(params[2]) if len(params) > 2 else 0
            full_name = params[3] if len(params) > 3 else None
            email = params[4] if len(params) > 4 else None
            phone = params[5] if len(params) > 5 else None
            add_user(username, is_admin, is_vip, full_name, email, phone)
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
            is_vip = int(params[2]) if len(params) > 2 else None
            full_name = params[3] if len(params) > 3 else None
            email = params[4] if len(params) > 4 else None
            phone = params[5] if len(params) > 5 else None
            update_user(username, is_admin, is_vip, full_name, email, phone)
            bot.reply_to(message, f"Zaktualizowano dane użytkownika {username}.")

    @bot.message_handler(commands=['listwhitelist'])
    def list_whitelist(message):
        if not is_user_admin(message.from_user.username):
            bot.reply_to(message, "Nie masz uprawnień do zarządzania whitelistą.")
            return

        users = get_all_users()
        if not users:
            bot.reply_to(message, "Whitelist jest pusta.")
            return

        response = "Lista użytkowników w whiteliście:\n"
        for user in users:
            response += f"Username: {user[0]}, Admin: {'Yes' if user[1] else 'No'}, VIP: {'Yes' if user[2] else 'No'}, Full Name: {user[3]}, Email: {user[4]}, Phone: {user[5]}\n"

        bot.reply_to(message, response)
