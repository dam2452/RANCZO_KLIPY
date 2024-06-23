import sqlite3
from bot.config import USERS_DB


def init_db():
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            is_moderator INTEGER NOT NULL DEFAULT 0,
            full_name TEXT,
            email TEXT,
            phone TEXT
        )
    ''')
    conn.commit()
    conn.close()


def add_user(username, is_admin=0, is_moderator=0, full_name=None, email=None, phone=None):
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, is_admin, is_moderator, full_name, email, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, is_admin, is_moderator, full_name, email, phone))
    conn.commit()
    conn.close()


def update_user(username, is_admin=None, is_moderator=None, full_name=None, email=None, phone=None):
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    updates = []
    params = []

    if is_admin is not None:
        updates.append("is_admin = ?")
        params.append(is_admin)
    if is_moderator is not None:
        updates.append("is_moderator = ?")
        params.append(is_moderator)
    if full_name is not None:
        updates.append("full_name = ?")
        params.append(full_name)
    if email is not None:
        updates.append("email = ?")
        params.append(email)
    if phone is not None:
        updates.append("phone = ?")
        params.append(phone)

    params.append(username)
    cursor.execute(f'''
        UPDATE users
        SET {', '.join(updates)}
        WHERE username = ?
    ''', params)

    conn.commit()
    conn.close()


def remove_user(username):
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()


def get_all_users():
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT username, is_admin, is_moderator, full_name, email, phone FROM users')
    users = cursor.fetchall()
    conn.close()
    return users


def get_admin_users():
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT username, full_name, email, phone FROM users WHERE is_admin = 1')
    users = cursor.fetchall()
    conn.close()
    return users


def get_moderator_users():
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT username, full_name, email, phone FROM users WHERE is_moderator = 1')
    users = cursor.fetchall()
    conn.close()
    return users


def is_user_authorized(username):
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


def is_user_admin(username):
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT is_admin FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None and result[0] == 1


def is_user_moderator(username):
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute('SELECT is_moderator FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None and result[0] == 1

def set_default_admin(default_admin):
    conn = sqlite3.connect(USERS_DB)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, is_admin)
        VALUES (?, 1)
    ''', (default_admin,))
    conn.commit()
    conn.close()