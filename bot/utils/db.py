import asyncpg
from bot.config import POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT
# import psycopg2
# from psycopg2 import sql

async def get_db_connection():
    return await asyncpg.connect(
        host=POSTGRES_HOST,
        port=POSTGRES_PORT,
        database=POSTGRES_DB,
        user=POSTGRES_USER,
        password=POSTGRES_PASSWORD
    )

async def init_db():
    conn = await get_db_connection()
    async with conn.transaction():
        await conn.execute('''
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
        await conn.execute('''
            CREATE TABLE IF NOT EXISTS clips (
                id SERIAL PRIMARY KEY,
                username TEXT NOT NULL,
                clip_name TEXT NOT NULL,
                video_data BYTEA NOT NULL,
                start_time INT,
                end_time INT,
                season INT,
                episode_number INT,
                is_compilation BOOLEAN NOT NULL DEFAULT FALSE,
                FOREIGN KEY (username) REFERENCES users (username)
            )
        ''')
    await conn.close()

async def add_user(username, is_admin=False, is_moderator=False, full_name=None, email=None, phone=None):
    conn = await get_db_connection()
    async with conn.transaction():
        await conn.execute('''
            INSERT INTO users (username, is_admin, is_moderator, full_name, email, phone)
            VALUES ($1, $2, $3, $4, $5, $6)
            ON CONFLICT (username) DO NOTHING
        ''', username, is_admin, is_moderator, full_name, email, phone)
    await conn.close()

async def update_user(username, is_admin=None, is_moderator=None, full_name=None, email=None, phone=None):
    conn = await get_db_connection()
    updates = []
    params = []

    if is_admin is not None:
        updates.append('is_admin = $' + str(len(params) + 1))
        params.append(is_admin)
    if is_moderator is not None:
        updates.append('is_moderator = $' + str(len(params) + 1))
        params.append(is_moderator)
    if full_name is not None:
        updates.append('full_name = $' + str(len(params) + 1))
        params.append(full_name)
    if email is not None:
        updates.append('email = $' + str(len(params) + 1))
        params.append(email)
    if phone is not None:
        updates.append('phone = $' + str(len(params) + 1))
        params.append(phone)

    if updates:
        query = f'UPDATE users SET {", ".join(updates)} WHERE username = ${len(params) + 1}'
        params.append(username)
        async with conn.transaction():
            await conn.execute(query, *params)

    await conn.close()


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


async def is_user_authorized(username):
    conn = await get_db_connection()
    result = await conn.fetchval('SELECT COUNT(*) FROM users WHERE username = $1', username)
    await conn.close()
    return result > 0


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


async def set_default_admin(admin_id):
    conn = await get_db_connection()
    await conn.execute('''
        INSERT INTO users (username, is_admin)
        VALUES ($1, TRUE)
        ON CONFLICT (username) DO NOTHING
    ''', admin_id)
    await conn.close()

def get_saved_clips(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT clip_name, start_time, end_time, season, episode_number, is_compilation FROM clips WHERE username = %s', (username,))
    clips = cursor.fetchall()
    cursor.close()
    conn.close()
    return clips

async def save_clip(username, clip_name, video_data, start_time, end_time, season, episode_number, is_compilation=False):
    conn = await get_db_connection()
    async with conn.transaction():
        await conn.execute('''
            INSERT INTO clips (username, clip_name, video_data, start_time, end_time, season, episode_number, is_compilation)
            VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ''', username, clip_name, video_data, start_time, end_time, season, episode_number, is_compilation)
    await conn.close()

async def get_clip_by_name(username, clip_name):
    conn = await get_db_connection()
    result = await conn.fetchrow('''
        SELECT video_data, start_time, end_time
        FROM clips
        WHERE username = $1 AND clip_name = $2
    ''', username, clip_name)
    await conn.close()
    return result

async def get_clip_by_index(username, index):
    conn = await get_db_connection()
    clip = await conn.fetchrow('''
        SELECT clip_name, start_time, end_time, season, episode_number, is_compilation
        FROM clips
        WHERE username = $1
        ORDER BY id
        LIMIT 1 OFFSET $2
    ''', username, index - 1)
    await conn.close()

    if clip:
        clip_name, start_time, end_time, season, episode_number, is_compilation = clip
        return (clip_name, start_time, end_time, season, episode_number, is_compilation)
    return None

async def get_video_data_by_name(username, clip_name):
    conn = await get_db_connection()
    result = await conn.fetchval('''
        SELECT video_data
        FROM clips
        WHERE username = $1 AND clip_name = $2
    ''', username, clip_name)
    await conn.close()

    return result