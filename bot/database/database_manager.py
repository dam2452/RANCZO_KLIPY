from datetime import (
    date,
    timedelta,
)
from typing import (
    List,
    Optional,
    Tuple,
)

import asyncpg

from bot.database.user import User
from bot.settings import settings


class DatabaseManager:  # pylint: disable=too-many-public-methods
    @staticmethod
    async def get_db_connection() -> Optional[asyncpg.Connection]:
        return await asyncpg.connect(
            host=settings.POSTGRES_HOST,
            port=settings.POSTGRES_PORT,
            database=settings.POSTGRES_DB,
            user=settings.POSTGRES_USER,
            password=settings.POSTGRES_PASSWORD,
        )

    @staticmethod
    async def init_db() -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username TEXT UNIQUE NOT NULL,
                    is_admin BOOLEAN NOT NULL DEFAULT FALSE,
                    is_moderator BOOLEAN NOT NULL DEFAULT FALSE,
                    full_name TEXT,
                    email TEXT,
                    phone TEXT,
                    subscription_end DATE DEFAULT NULL
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS clips (
                    id SERIAL PRIMARY KEY,
                    chat_id BIGINT NOT NULL,
                    username TEXT NOT NULL,
                    clip_name TEXT NOT NULL,
                    video_data BYTEA NOT NULL,
                    start_time FLOAT,
                    end_time FLOAT,
                    duration FLOAT,
                    season INT,
                    episode_number INT,
                    is_compilation BOOLEAN NOT NULL DEFAULT FALSE,
                    FOREIGN KEY (username) REFERENCES users (username)
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS reports (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    report TEXT NOT NULL,
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (username) REFERENCES users (username)
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS user_logs (
                    id SERIAL PRIMARY KEY,
                    username TEXT NOT NULL,
                    command TEXT NOT NULL,
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS system_logs (
                    id SERIAL PRIMARY KEY,
                    log_level TEXT NOT NULL,
                    log_message TEXT NOT NULL,
                    timestamp TIMESTAMPTZ DEFAULT CURRENT_TIMESTAMP
                )
            ''')
        await conn.close()

    @staticmethod
    async def log_user_activity(username: str, command: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                '''
                INSERT INTO user_logs (username, command)
                VALUES ($1, $2)
            ''', username, command,
            )
        await conn.close()

    @staticmethod
    async def log_system_message(log_level: str, log_message: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                '''
                INSERT INTO system_logs (log_level, log_message)
                VALUES ($1, $2)
            ''', log_level, log_message,
            )
        await conn.close()

    @staticmethod
    async def add_user(user: User, subscription_days: Optional[int] = None) -> None:
        conn = await DatabaseManager.get_db_connection()
        subscription_end = date.today() + timedelta(days=subscription_days) if subscription_days else None
        async with conn.transaction():
            await conn.execute(
                '''
                INSERT INTO users (username, is_admin, is_moderator, full_name, email, phone, subscription_end)
                VALUES ($1, $2, $3, $4, $5, $6, $7)
                ON CONFLICT (username) DO NOTHING
            ''', user.name, bool(user.is_admin), bool(user.is_moderator), user.full_name, user.email, user.phone, subscription_end,
            )
        await conn.close()

    @staticmethod
    async def update_user(user: User, subscription_end: Optional[int] = None) -> None:
        conn = await DatabaseManager.get_db_connection()
        updates = []
        params = []

        if user.is_admin is not None:
            updates.append('is_admin = $' + str(len(params) + 1))
            params.append(bool(user.is_admin))
        if user.is_moderator is not None:
            updates.append('is_moderator = $' + str(len(params) + 1))
            params.append(bool(user.is_moderator))
        if user.full_name is not None:
            updates.append('full_name = $' + str(len(params) + 1))
            params.append(user.full_name)
        if user.email is not None:
            updates.append('email = $' + str(len(params) + 1))
            params.append(user.email)
        if user.phone is not None:
            updates.append('phone = $' + str(len(params) + 1))
            params.append(user.phone)
        if subscription_end is not None:
            updates.append('subscription_end = $' + str(len(params) + 1))
            params.append(subscription_end)

        if updates:
            query = f'UPDATE users SET {", ".join(updates)} WHERE username = ${len(params) + 1}'
            params.append(user.name)
            async with conn.transaction():
                await conn.execute(query, *params)

        await conn.close()

    @staticmethod
    async def remove_user(username: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute('DELETE FROM users WHERE username = $1', username)
        await conn.close()

    @staticmethod
    async def get_all_users() -> Optional[List[asyncpg.Record]]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetch(
            'SELECT username, is_admin, is_moderator, full_name, email, phone, subscription_end FROM users',
        )
        await conn.close()
        return result

    @staticmethod
    async def is_user_in_db(username: str) -> bool:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetch("SELECT EXISTS (SELECT 1 FROM users where username = $1)", username)
        await conn.close()
        return result[0]['exists']

    @staticmethod
    async def get_admin_users() -> Optional[List[asyncpg.Record]]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetch('SELECT username, full_name, email, phone FROM users WHERE is_admin = TRUE')
        await conn.close()
        return result

    @staticmethod
    async def get_moderator_users() -> Optional[List[asyncpg.Record]]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetch('SELECT username, full_name, email, phone FROM users WHERE is_moderator = TRUE')
        await conn.close()
        return result

    @staticmethod
    async def is_user_subscribed(username: str) -> bool:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchrow(
            'SELECT is_admin, is_moderator, subscription_end FROM users WHERE username = $1',
            username,
        )
        await conn.close()
        if result:
            is_admin = result['is_admin']
            is_moderator = result['is_moderator']
            subscription_end = result['subscription_end']
            if is_admin or is_moderator or (subscription_end and subscription_end >= date.today()):
                return True
        return False

    @staticmethod
    async def is_user_admin(username: str) -> Optional[bool]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval('SELECT is_admin FROM users WHERE username = $1', username)
        await conn.close()
        return result

    @staticmethod
    async def is_user_moderator(username: str) -> Optional[bool]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval('SELECT is_moderator FROM users WHERE username = $1', username)
        await conn.close()
        return result

    @staticmethod
    async def set_default_admin(admin_id: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            '''
            INSERT INTO users (username, is_admin)
            VALUES ($1, TRUE)
            ON CONFLICT (username) DO NOTHING
        ''', admin_id,
        )
        await conn.close()

    @staticmethod
    async def get_saved_clips(username: str) -> Optional[List[asyncpg.Record]]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetch(
            'SELECT clip_name, start_time, end_time, duration, season, episode_number, is_compilation FROM clips WHERE username = $1',
            username,
        )
        await conn.close()
        return result

    @staticmethod
    async def save_clip(
            chat_id: int, username: str, clip_name: str, video_data: bytes, start_time: float, end_time: float, duration: float, is_compilation: bool,
            season: Optional[int] = None, episode_number: Optional[int] = None,
    ) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                """
                INSERT INTO clips (chat_id, username, clip_name, video_data, start_time, end_time, duration, season, episode_number, is_compilation)
                VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9 , $10)
                """,
                chat_id, username, clip_name, video_data, start_time, end_time, duration, season, episode_number, is_compilation,
            )
        await conn.close()

    @staticmethod
    async def get_clip_by_name(username: str, clip_name: str) -> Optional[Tuple[bytes, int, int]]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchrow(
            '''
            SELECT video_data, duration
            FROM clips
            WHERE username = $1 AND clip_name = $2
        ''', username, clip_name,
        )
        await conn.close()
        return result

    @staticmethod
    async def get_clip_by_index(username: str, index: int) -> Optional[Tuple[str, int, int, int, int, bool]]:
        conn = await DatabaseManager.get_db_connection()
        clip = await conn.fetchrow(
            '''
            SELECT clip_name, duration, season, episode_number, is_compilation
            FROM clips
            WHERE username = $1
            ORDER BY id
            LIMIT 1 OFFSET $2
        ''', username, index - 1,
        )
        await conn.close()

        if clip:
            clip_name, start_time, end_time, season, episode_number, is_compilation = clip
            return clip_name, start_time, end_time, season, episode_number, is_compilation
        return None

    @staticmethod
    async def get_video_data_by_name(username: str, clip_name: str) -> Optional[bytes]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval(
            '''
            SELECT video_data
            FROM clips
            WHERE username = $1 AND clip_name = $2
        ''', username, clip_name,
        )
        await conn.close()

        return result

    @staticmethod
    async def add_subscription(username: str, days: int) -> Optional[date]:
        conn = await DatabaseManager.get_db_connection()
        new_end_date = await conn.fetchval(
            '''
            UPDATE users
            SET subscription_end = COALESCE(subscription_end, CURRENT_DATE) + $1 * INTERVAL '1 day'
            WHERE username = $2
            RETURNING subscription_end
        ''', days, username,
        )
        await conn.close()
        return new_end_date

    @staticmethod
    async def remove_subscription(username: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            '''
            UPDATE users
            SET subscription_end = NULL
            WHERE username = $1
        ''', username,
        )
        await conn.close()

    @staticmethod
    async def get_user_subscription(username: str) -> Optional[date]:
        conn = await DatabaseManager.get_db_connection()
        subscription_end = await conn.fetchval('SELECT subscription_end FROM users WHERE username = $1', username)
        await conn.close()
        return subscription_end

    @staticmethod
    async def add_report(username: str, report: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                '''
                INSERT INTO reports (username, report)
                VALUES ($1, $2)
            ''', username, report,
            )
        await conn.close()

    @staticmethod
    async def delete_clip(username: str, clip_name: str) -> str:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            result = await conn.execute(
                '''
                DELETE FROM clips
                WHERE username = $1 AND clip_name = $2
            ''', username, clip_name,
            )
        await conn.close()
        return result

    @staticmethod
    async def is_clip_name_unique(chat_id: int, clip_name: str) -> bool:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval(
            'SELECT COUNT(*) FROM clips WHERE chat_id=$1 AND clip_name=$2',
            chat_id, clip_name,
        )
        await conn.close()
        return result == 0
