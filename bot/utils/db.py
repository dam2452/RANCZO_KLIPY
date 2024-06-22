import sqlite3
import os

def init_db():
    conn = sqlite3.connect('whitelist.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            is_admin INTEGER NOT NULL DEFAULT 0,
            is_vip INTEGER NOT NULL DEFAULT 0,
            full_name TEXT,
            email TEXT,
            phone TEXT
        )
    ''')
    conn.commit()
    conn.close()

def add_user(username, is_admin=0, is_vip=0, full_name=None, email=None, phone=None):
    conn = sqlite3.connect('whitelist.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR IGNORE INTO users (username, is_admin, is_vip, full_name, email, phone)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, is_admin, is_vip, full_name, email, phone))
    conn.commit()
    conn.close()

def update_user(username, is_admin=None, is_vip=None, full_name=None, email=None, phone=None):
    conn = sqlite3.connect('whitelist.db')
    cursor = conn.cursor()
    updates = []
    params = []

    if is_admin is not None:
        updates.append("is_admin = ?")
        params.append(is_admin)
    if is_vip is not None:
        updates.append("is_vip = ?")
        params.append(is_vip)
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
    conn = sqlite3.connect('whitelist.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = ?', (username,))
    conn.commit()
    conn.close()

def get_all_users():
    conn = sqlite3.connect('whitelist.db')
    cursor = conn.cursor()
    cursor.execute('SELECT username, is_admin, is_vip, full_name, email, phone FROM users')
    users = cursor.fetchall()
    conn.close()
    return users

def is_user_authorized(username):
    conn = sqlite3.connect('whitelist.db')
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None

def is_user_admin(username):
    conn = sqlite3.connect('whitelist.db')
    cursor = conn.cursor()
    cursor.execute('SELECT is_admin FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None and result[0] == 1

def is_user_vip(username):
    conn = sqlite3.connect('whitelist.db')
    cursor = conn.cursor()
    cursor.execute('SELECT is_vip FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    conn.close()
    return result is not None and result[0] == 1

def sync_admins_from_file(admins_file):
    with open(admins_file, 'r') as f:
        admins = f.read().splitlines()
    for admin in admins:
        add_user(admin, is_admin=1)

def sync_vips_from_file(vips_file):
    with open(vips_file, 'r') as f:
        vips = f.read().splitlines()
    for vip in vips:
        add_user(vip, is_vip=1)
