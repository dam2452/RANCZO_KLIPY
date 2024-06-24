import psycopg2
from psycopg2 import sql
from bot.config import POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT


def get_db_connection():
    #port add
    return psycopg2.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            is_admin BOOLEAN NOT NULL DEFAULT FALSE,
            is_moderator BOOLEAN NOT NULL DEFAULT FALSE,
            full_name TEXT,
            email TEXT,
            phone TEXT
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()


def add_user(username, is_admin=False, is_moderator=False, full_name=None, email=None, phone=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, is_admin, is_moderator, full_name, email, phone)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (username) DO NOTHING
    ''', (username, is_admin, is_moderator, full_name, email, phone))
    conn.commit()
    cursor.close()
    conn.close()


def update_user(username, is_admin=None, is_moderator=None, full_name=None, email=None, phone=None):
    conn = get_db_connection()
    cursor = conn.cursor()
    updates = []
    params = []

    if is_admin is not None:
        updates.append("is_admin = %s")
        params.append(is_admin)
    if is_moderator is not None:
        updates.append("is_moderator = %s")
        params.append(is_moderator)
    if full_name is not None:
        updates.append("full_name = %s")
        params.append(full_name)
    if email is not None:
        updates.append("email = %s")
        params.append(email)
    if phone is not None:
        updates.append("phone = %s")
        params.append(phone)

    params.append(username)
    query = sql.SQL('UPDATE users SET {} WHERE username = %s').format(sql.SQL(', ').join(map(sql.SQL, updates)))
    cursor.execute(query, params)

    conn.commit()
    cursor.close()
    conn.close()


def remove_user(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('DELETE FROM users WHERE username = %s', (username,))
    conn.commit()
    cursor.close()
    conn.close()


def get_all_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, is_admin, is_moderator, full_name, email, phone FROM users')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users


def get_admin_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, full_name, email, phone FROM users WHERE is_admin = TRUE')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users


def get_moderator_users():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT username, full_name, email, phone FROM users WHERE is_moderator = TRUE')
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    return users


def is_user_authorized(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT 1 FROM users WHERE username = %s', (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None


def is_user_admin(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT is_admin FROM users WHERE username = %s', (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None and result[0]


def is_user_moderator(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT is_moderator FROM users WHERE username = %s', (username,))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result is not None and result[0]


def set_default_admin(default_admin):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO users (username, is_admin)
        VALUES (%s, TRUE)
        ON CONFLICT (username) DO NOTHING
    ''', (default_admin,))
    conn.commit()
    cursor.close()
    conn.close()
