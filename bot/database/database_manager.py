from datetime import (
    date,
    timedelta,
)
import json
from typing import (
    List,
    Optional,
    Tuple,
)

from aiogram import Bot
import asyncpg

from bot.database.models import (
    LastClip,
    UserProfile,
    VideoClip,
)
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
    async def execute_sql_file(file_path: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            with open(file_path, 'r', encoding='utf-8') as file:
                sql = file.read()
                await conn.execute(sql)
        await conn.close()

    @staticmethod
    async def init_db() -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            try:
                table_exists = await conn.fetchval(
                    "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = $1)",
                    'user_profiles',
                )

                if not table_exists:
                    with open('./bot/database/init_db.sql', 'r', encoding='utf-8') as file:
                        sql = file.read()
                        await conn.execute(sql)
                else:
                    print("Database is already initialized. Skipping initialization script.")
            except asyncpg.PostgresError as e:
                print(f"Error during database initialization: {e}")
        await conn.close()

    @staticmethod
    async def log_user_activity(user_id: int, command: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                'INSERT INTO user_logs (user_id, command) VALUES ($1, $2)',
                user_id, command,
            )
        await conn.close()

    @staticmethod
    async def log_system_message(log_level: str, log_message: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                'INSERT INTO system_logs (log_level, log_message) VALUES ($1, $2)',
                log_level, log_message,
            )
        await conn.close()

    @staticmethod
    async def add_user(user: UserProfile, bot: Bot, subscription_days: Optional[int] = None) -> None:
        conn = await DatabaseManager.get_db_connection()

        # Pobierz username i full_name na podstawie user_id, jeśli nie są dostarczone w UserProfile
        if not user.username or not user.full_name:
            user_data = await bot.get_chat(user.user_id)
            user.username = user_data.username
            user.full_name = user_data.full_name

        subscription_end = date.today() + timedelta(days=subscription_days) if subscription_days else None
        async with conn.transaction():
            await conn.execute(
                'INSERT INTO user_profiles (user_id, username, full_name, subscription_end, note) VALUES ($1, $2, $3, $4, $5) ON CONFLICT (user_id) DO NOTHING',
                user.user_id, user.username, user.full_name, subscription_end, user.note,
            )
        await conn.close()

    @staticmethod
    async def update_user(user: UserProfile, subscription_end: Optional[int] = None) -> None:
        conn = await DatabaseManager.get_db_connection()
        updates = []
        params = []

        if user.username is not None:
            updates.append(f'username = ${len(params) + 1}')
            params.append(user.username)
        if user.full_name is not None:
            updates.append(f'full_name = ${len(params) + 1}')
            params.append(user.full_name)
        if user.note is not None:
            updates.append(f'note = ${len(params) + 1}')
            params.append(user.note)
        if subscription_end is not None:
            updates.append(f'subscription_end = ${len(params) + 1}')
            params.append(subscription_end)

        if updates:
            query = f'UPDATE user_profiles SET {", ".join(updates)} WHERE user_id = ${len(params) + 1}'
            params.append(user.user_id)
            async with conn.transaction():
                await conn.execute(query, *params)

        await conn.close()

    @staticmethod
    async def remove_user(user_id: int) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute('DELETE FROM user_profiles WHERE user_id = $1', user_id)
        await conn.close()

    @staticmethod
    async def get_all_users() -> Optional[List[UserProfile]]:
        conn = await DatabaseManager.get_db_connection()
        rows = await conn.fetch(
            'SELECT user_id, username, subscription_end, note FROM user_profiles',
        )
        await conn.close()
        return [UserProfile(**row) for row in rows] if rows else None

    @staticmethod
    async def is_user_in_db(user_id: int) -> bool:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval("SELECT EXISTS (SELECT 1 FROM user_profiles WHERE user_id = $1)", user_id)
        await conn.close()
        return result

    @staticmethod
    async def get_admin_users() -> Optional[List[UserProfile]]:
        conn = await DatabaseManager.get_db_connection()
        rows = await conn.fetch(
            'SELECT user_id, username, subscription_end, note FROM user_profiles WHERE user_id IN (SELECT user_id FROM user_roles WHERE is_admin = TRUE)',
        )
        await conn.close()
        return [UserProfile(**row) for row in rows] if rows else None

    @staticmethod
    async def get_moderator_users() -> Optional[List[UserProfile]]:
        conn = await DatabaseManager.get_db_connection()
        rows = await conn.fetch(
            'SELECT user_id, username, subscription_end, note FROM user_profiles WHERE user_id IN (SELECT user_id FROM user_roles WHERE is_moderator = TRUE)',
        )
        await conn.close()
        return [UserProfile(**row) for row in rows] if rows else None

    @staticmethod
    async def is_user_subscribed(user_id: int) -> bool:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchrow(
            '''
            SELECT ur.is_admin, ur.is_moderator, up.subscription_end
            FROM user_profiles up
            LEFT JOIN user_roles ur ON ur.user_id = up.user_id
            WHERE up.user_id = $1
            ''',
            user_id,
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
    async def is_user_admin(user_id: int) -> Optional[bool]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval(
            'SELECT is_admin FROM user_roles WHERE user_id = $1',
            user_id,
        )
        await conn.close()
        return result

    @staticmethod
    async def is_user_moderator(user_id: int) -> Optional[bool]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval(
            'SELECT is_moderator FROM user_roles WHERE user_id = $1',
            user_id,
        )
        await conn.close()
        return result

    @staticmethod
    async def set_default_admin(user_id: int, bot: Bot) -> None:
        conn = await DatabaseManager.get_db_connection()

        # Pobierz username i full_name na podstawie user_id
        user_data = await bot.get_chat(user_id)
        username = user_data.username
        full_name = user_data.full_name

        await conn.execute(
            '''
            INSERT INTO user_profiles (user_id, username, full_name)
            VALUES ($1, $2, $3)
            ON CONFLICT (user_id) DO NOTHING
            ''', user_id, username, full_name,
        )
        await conn.execute(
            '''
            INSERT INTO user_roles (user_id, is_admin)
            VALUES ($1, TRUE)
            ON CONFLICT (user_id) DO NOTHING
            ''', user_id,
        )
        await conn.close()

    @staticmethod
    async def get_saved_clips(user_id: int) -> Optional[List[VideoClip]]:
        conn = await DatabaseManager.get_db_connection()
        rows = await conn.fetch(
            'SELECT clip_name, start_time, end_time, duration, season, episode_number, is_compilation FROM video_clips WHERE user_id = $1',
            user_id,
        )
        await conn.close()
        return [VideoClip(**row) for row in rows] if rows else None

    @staticmethod
    async def save_clip(
        chat_id: int, user_id: int, clip_name: str, video_data: bytes, start_time: float,
        end_time: float, duration: float, is_compilation: bool,
        season: Optional[int] = None, episode_number: Optional[int] = None,
    ) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                'INSERT INTO video_clips (chat_id, user_id, clip_name, video_data, start_time, '
                'end_time, duration, season, episode_number, is_compilation) '
                'VALUES ($1, $2, $3, $4::bytea, $5, $6, $7, $8, $9, $10)',
                chat_id, user_id, clip_name, video_data, start_time, end_time, duration,
                season, episode_number, is_compilation,
            )
        await conn.close()

    @staticmethod
    async def get_clip_by_name(user_id: int, clip_name: str) -> Optional[Tuple[bytes, int, int]]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchrow(
            'SELECT video_data, duration FROM video_clips WHERE user_id = $1 AND clip_name = $2',
            user_id, clip_name,
        )
        await conn.close()
        return result

    @staticmethod
    async def get_clip_by_index(user_id: int, index: int) -> Optional[Tuple[str, int, int, int, int, bool]]:
        conn = await DatabaseManager.get_db_connection()
        clip = await conn.fetchrow(
            '''
            SELECT clip_name, duration, season, episode_number, is_compilation
            FROM video_clips
            WHERE user_id = $1
            ORDER BY id
            LIMIT 1 OFFSET $2
            ''', user_id, index - 1,
        )
        await conn.close()

        if clip:
            clip_name, duration, season, episode_number, is_compilation = clip
            return clip_name, duration, season, episode_number, is_compilation
        return None

    @staticmethod
    async def get_video_data_by_name(user_id: int, clip_name: str) -> Optional[bytes]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval(
            'SELECT video_data FROM video_clips WHERE user_id = $1 AND clip_name = $2',
            user_id, clip_name,
        )
        await conn.close()
        return result

    @staticmethod
    async def add_subscription(user_id: int, days: int) -> Optional[date]:
        conn = await DatabaseManager.get_db_connection()
        new_end_date = await conn.fetchval(
            '''
            UPDATE user_profiles
            SET subscription_end = COALESCE(subscription_end, CURRENT_DATE) + $1 * INTERVAL '1 day'
            WHERE user_id = $2
            RETURNING subscription_end
            ''', days, user_id,
        )
        await conn.close()
        return new_end_date

    @staticmethod
    async def remove_subscription(user_id: int) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            '''
            UPDATE user_profiles
            SET subscription_end = NULL
            WHERE user_id = $1
            ''', user_id,
        )
        await conn.close()

    @staticmethod
    async def get_user_subscription(user_id: int) -> Optional[date]:
        conn = await DatabaseManager.get_db_connection()
        subscription_end = await conn.fetchval('SELECT subscription_end FROM user_profiles WHERE user_id = $1', user_id)
        await conn.close()
        return subscription_end

    @staticmethod
    async def add_report(user_id: int, report: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                '''
                INSERT INTO reports (user_id, report)
                VALUES ($1, $2)
                ''', user_id, report,
            )
        await conn.close()

    @staticmethod
    async def delete_clip(user_id: int, clip_name: str) -> str:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            result = await conn.execute(
                '''
                DELETE FROM video_clips
                WHERE user_id = $1 AND clip_name = $2
                ''', user_id, clip_name,
            )
        await conn.close()
        return result

    @staticmethod
    async def is_clip_name_unique(chat_id: int, clip_name: str) -> bool:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval(
            'SELECT COUNT(*) FROM video_clips WHERE chat_id=$1 AND clip_name=$2',
            chat_id, clip_name,
        )
        await conn.close()
        return result == 0

    @staticmethod
    async def insert_last_search(chat_id: int, quote: str, segments: Optional[dict,json]) -> int:
        conn = await DatabaseManager.get_db_connection()
        search_id = await conn.fetchval(
            'INSERT INTO search_history (chat_id, quote, segments) VALUES ($1, $2, $3::jsonb) RETURNING id',
            chat_id, quote, segments,
        )
        await conn.close()
        return search_id

    @staticmethod
    async def get_last_search_by_chat_id(chat_id: int) -> Optional[asyncpg.Record]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchrow(
            '''
            SELECT id, chat_id, quote, segments
            FROM search_history
            WHERE chat_id = $1
            ORDER BY id DESC
            LIMIT 1
            ''', chat_id,
        )
        await conn.close()
        return result

    @staticmethod
    async def update_last_search(search_id: int, new_quote: Optional[str] = None, new_segments: Optional[dict] = None) -> None:
        conn = await DatabaseManager.get_db_connection()
        if new_quote:
            await conn.execute(
                '''
                UPDATE search_history
                SET quote = $1
                WHERE id = $2
                ''', new_quote, search_id,
            )
        if new_segments:
            await conn.execute(
                '''
                UPDATE search_history
                SET segments = $1::jsonb
                WHERE id = $2
                ''', new_segments, search_id,
            )
        await conn.close()

    @staticmethod
    async def delete_last_search(search_id: int) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            '''
            DELETE FROM search_history
            WHERE id = $1
            ''', search_id,
        )
        await conn.close()

    @staticmethod
    async def insert_last_clip(
        chat_id: int, segment: Optional[dict] = None, compiled_clip: Optional[bytes] = None, clip_type: Optional[str] = None,
        adjusted_start_time: Optional[float] = None, adjusted_end_time: Optional[float] = None,
        is_adjusted: bool = False,
    ) -> int:
        conn = await DatabaseManager.get_db_connection()
        clip_id = await conn.fetchval(
            'INSERT INTO last_clips (chat_id, segment, compiled_clip, type, adjusted_start_time, adjusted_end_time, is_adjusted) VALUES ($1, $2::jsonb, $3::bytea, $4, $5, $6, $7) RETURNING id',
            chat_id, segment, compiled_clip, clip_type, adjusted_start_time, adjusted_end_time, is_adjusted,
        )
        await conn.close()
        return clip_id

    @staticmethod
    async def get_last_clip_by_chat_id(chat_id: int) -> Optional[LastClip]:
        conn = await DatabaseManager.get_db_connection()
        row = await conn.fetchrow(
            '''
            SELECT id, chat_id, segment, compiled_clip, type AS clip_type, adjusted_start_time, adjusted_end_time, is_adjusted, timestamp
            FROM last_clips
            WHERE chat_id = $1
            ORDER BY id DESC
            LIMIT 1
            ''', chat_id,
        )
        return LastClip(**row) if row else None

    @staticmethod
    async def update_last_clip(
        clip_id: int, new_segment: Optional[dict] = None, new_compiled_clip: Optional[bytes] = None,
        new_type: Optional[str] = None,
    ) -> None:
        conn = await DatabaseManager.get_db_connection()
        if new_segment:
            await conn.execute(
                '''
                UPDATE last_clips
                SET segment = $1::jsonb
                WHERE id = $2
                ''', new_segment, clip_id,
            )
        if new_compiled_clip:
            await conn.execute(
                '''
                UPDATE last_clips
                SET compiled_clip = $1::bytea
                WHERE id = $2
                ''', new_compiled_clip, clip_id,
            )
        if new_type:
            await conn.execute(
                '''
                UPDATE last_clips
                SET type = $1
                WHERE id = $2
                ''', new_type, clip_id,
            )
        await conn.close()

    @staticmethod
    async def delete_last_clip(clip_id: int) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            '''
            DELETE FROM last_clips
            WHERE id = $1
            ''', clip_id,
        )
        await conn.close()

    @staticmethod
    async def get_user_id_by_username(username: str) -> Optional[int]:
        conn = await DatabaseManager.get_db_connection()
        user_id = await conn.fetchval('SELECT user_id FROM user_profiles WHERE username = $1', username)
        await conn.close()
        return user_id
