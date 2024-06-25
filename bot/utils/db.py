import psycopg2
from psycopg2 import sql
from bot.config import POSTGRES_HOST, POSTGRES_DB, POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_PORT

def get_db_connection():
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
    cursor.execute('''
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

def get_saved_clips(username):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('SELECT clip_name, start_time, end_time, season, episode_number, is_compilation FROM clips WHERE username = %s', (username,))
    clips = cursor.fetchall()
    cursor.close()
    conn.close()
    return clips

def save_clip(username, clip_name, video_data, start_time, end_time, season, episode_number, is_compilation=False):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO clips (username, clip_name, video_data, start_time, end_time, season, episode_number, is_compilation)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    ''', (username, clip_name, psycopg2.Binary(video_data), start_time, end_time, season, episode_number, is_compilation))
    conn.commit()
    cursor.close()
    conn.close()

def get_clip_by_name(username, clip_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    query = '''
        SELECT video_data, start_time, end_time
        FROM clips
        WHERE username = %s AND clip_name = %s
    '''
    cursor.execute(query, (username, clip_name))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return result

def get_clip_by_index(username, index):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT clip_name, start_time, end_time, season, episode_number, is_compilation
        FROM clips
        WHERE username = %s
        ORDER BY id
        LIMIT 1 OFFSET %s
    ''', (username, index - 1))
    clip = cursor.fetchone()
    cursor.close()
    conn.close()

    if clip:
        clip_name, start_time, end_time, season, episode_number, is_compilation = clip
        return (clip_name, start_time, end_time, season, episode_number, is_compilation)
    return None

def get_video_data_by_name(username, clip_name):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT video_data
        FROM clips
        WHERE username = %s AND clip_name = %s
    ''', (username, clip_name))
    result = cursor.fetchone()
    cursor.close()
    conn.close()

    if result:
        return result[0]
    return None