from datetime import (
    date,
    datetime,
    timedelta,
)
import json
from typing import (
    List,
    Optional,
)

from aiogram import Bot
import asyncpg

from bot.database.models import (
    ClipType,
    LastClip,
    SearchHistory,
    SubscriptionKey,
    UserMessage,
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
            with open(file_path, "r", encoding="utf-8") as file:
                sql = file.read()
                await conn.execute(sql)
        await conn.close()

    @staticmethod
    async def init_db() -> None:
        conn = await DatabaseManager.get_db_connection()
        await DatabaseManager.execute_sql_file("./bot/database/init_db.sql")
        await conn.close()

    @staticmethod
    async def log_user_activity(user_id: int, command: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO user_logs (user_id, command) VALUES ($1, $2)",
                user_id, command,
            )
        await conn.close()

    @staticmethod
    async def log_system_message(log_level: str, log_message: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO system_logs (log_level, log_message) VALUES ($1, $2)",
                log_level, log_message,
            )
        await conn.close()

    @staticmethod
    async def add_user(
            user_id: int, username: Optional[str], full_name: Optional[str], note: Optional[str], bot: Bot,
            subscription_days: Optional[int] = None,
    ) -> None:
        conn = await DatabaseManager.get_db_connection()

        if not username or not full_name:
            user_data = await bot.get_chat(user_id)
            username = user_data.username
            full_name = user_data.full_name

        subscription_end = date.today() + timedelta(days=subscription_days) if subscription_days else None
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO user_profiles (user_id, username, full_name, subscription_end, note) "
                "VALUES ($1, $2, $3, $4, $5) "
                "ON CONFLICT (user_id) DO NOTHING",
                user_id, username, full_name, subscription_end, note,
            )
        await conn.close()

    @staticmethod
    async def update_user(
            user_id: int, username: Optional[str] = None, full_name: Optional[str] = None, note: Optional[str] = None,
            subscription_end: Optional[int] = None,
    ) -> None:
        conn = await DatabaseManager.get_db_connection()
        updates = []
        params = []

        if username is not None:
            updates.append(f"username = ${len(params) + 1}")
            params.append(username)
        if full_name is not None:
            updates.append(f"full_name = ${len(params) + 1}")
            params.append(full_name)
        if note is not None:
            updates.append(f"note = ${len(params) + 1}")
            params.append(note)
        if subscription_end is not None:
            updates.append(f"subscription_end = ${len(params) + 1}")
            params.append(subscription_end)

        if updates:
            query = f"UPDATE user_profiles SET {", ".join(updates)} WHERE user_id = ${len(params) + 1}"
            params.append(user_id)
            async with conn.transaction():
                await conn.execute(query, *params)

        await conn.close()

    @staticmethod
    async def remove_user(user_id: int) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute("DELETE FROM user_profiles WHERE user_id = $1", user_id)
        await conn.close()

    @staticmethod
    async def get_all_users() -> Optional[List[UserProfile]]:
        conn = await DatabaseManager.get_db_connection()
        rows = await conn.fetch(
            "SELECT user_id, username, full_name, subscription_end, note FROM user_profiles",
        )
        await conn.close()

        return [
            UserProfile(
                user_id=row["user_id"],
                username=row["username"],
                full_name=row["full_name"],
                subscription_end=row["subscription_end"],
                note=row["note"],
            ) for row in rows
        ] if rows else None

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
            "SELECT user_id, username, full_name, subscription_end, note FROM user_profiles "
            "WHERE user_id IN (SELECT user_id FROM user_roles WHERE is_admin = TRUE)",
        )
        await conn.close()
        return [
            UserProfile(
                user_id=row["user_id"],
                username=row["username"],
                full_name=row.get("full_name", "N/A"),
                subscription_end=row.get("subscription_end", None),
                note=row.get("note", "Brak"),
            ) for row in rows
        ] if rows else None

    @staticmethod
    async def get_moderator_users() -> Optional[List[UserProfile]]:
        conn = await DatabaseManager.get_db_connection()
        rows = await conn.fetch(
            "SELECT user_id, username, full_name, subscription_end, note FROM user_profiles "
            "WHERE user_id IN (SELECT user_id FROM user_roles WHERE is_moderator = TRUE)",
        )
        await conn.close()
        return [
            UserProfile(
                user_id=row["user_id"],
                username=row["username"],
                full_name=row.get("full_name", "N/A"),
                subscription_end=row.get("subscription_end", None),
                note=row.get("note", "Brak"),
            ) for row in rows
        ] if rows else None

    @staticmethod
    async def is_user_subscribed(user_id: int) -> bool:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchrow(
            "SELECT ur.is_admin, ur.is_moderator, up.subscription_end "
            "FROM user_profiles up "
            "LEFT JOIN user_roles ur ON ur.user_id = up.user_id "
            "WHERE up.user_id = $1",
            user_id,
        )
        await conn.close()
        if result:
            is_admin = result["is_admin"]
            is_moderator = result["is_moderator"]
            subscription_end = result["subscription_end"]
            if is_admin or is_moderator or (subscription_end and subscription_end >= date.today()):
                return True
        return False

    @staticmethod
    async def is_user_admin(user_id: int) -> Optional[bool]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval(
            "SELECT is_admin FROM user_roles WHERE user_id = $1",
            user_id,
        )
        await conn.close()
        return result

    @staticmethod
    async def is_user_moderator(user_id: int) -> Optional[bool]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval(
            "SELECT is_moderator FROM user_roles WHERE user_id = $1",
            user_id,
        )
        await conn.close()
        return result

    @staticmethod
    async def set_default_admin(user_id: int, bot: Bot) -> None:
        conn = await DatabaseManager.get_db_connection()

        user_data = await bot.get_chat(user_id)
        username = user_data.username
        full_name = user_data.full_name

        await conn.execute(
            "INSERT INTO user_profiles (user_id, username, full_name) "
            "VALUES ($1, $2, $3) "
            "ON CONFLICT (user_id) DO NOTHING",
            user_id, username, full_name,
        )
        await conn.execute(
            "INSERT INTO user_roles (user_id, is_admin) "
            "VALUES ($1, TRUE) "
            "ON CONFLICT (user_id) DO NOTHING",
            user_id,
        )
        await conn.close()

    @staticmethod
    def _row_to_video_clip(row: asyncpg.Record) -> VideoClip:
        return VideoClip(
            id=row["id"],
            chat_id=row["chat_id"],
            user_id=row["user_id"],
            clip_name=row["clip_name"],
            video_data=row["video_data"],
            start_time=row["start_time"],
            end_time=row["end_time"],
            duration=row["duration"],
            season=row["season"],
            episode_number=row["episode_number"],
            is_compilation=row["is_compilation"],
        )

    @staticmethod
    async def get_saved_clips(user_id: int) -> Optional[List[VideoClip]]:
        conn = await DatabaseManager.get_db_connection()
        rows = await conn.fetch(
            "SELECT id, chat_id, user_id, clip_name, video_data, start_time, end_time, duration, season, episode_number, is_compilation "
            "FROM video_clips "
            "WHERE user_id = $1",
            user_id,
        )
        await conn.close()

        if rows:
            return [DatabaseManager._row_to_video_clip(row) for row in rows]
        return None

    @staticmethod
    async def save_clip(
            chat_id: int, user_id: int, clip_name: str, video_data: bytes, start_time: float,
            end_time: float, duration: float, is_compilation: bool,
            season: Optional[int] = None, episode_number: Optional[int] = None,
    ) -> None:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            await conn.execute(
                "INSERT INTO video_clips (chat_id, user_id, clip_name, video_data, start_time, "
                "end_time, duration, season, episode_number, is_compilation) "
                "VALUES ($1, $2, $3, $4::bytea, $5, $6, $7, $8, $9, $10)",
                chat_id, user_id, clip_name, video_data, start_time, end_time, duration,
                season, episode_number, is_compilation,
            )
        await conn.close()

    @staticmethod
    async def get_clip_by_name(user_id: int, clip_name: str) -> Optional[VideoClip]:
        conn = await DatabaseManager.get_db_connection()
        row = await conn.fetchrow(
            "SELECT id, chat_id, user_id, clip_name, video_data, start_time, end_time, duration, season, episode_number, is_compilation "
            "FROM video_clips "
            "WHERE user_id = $1 AND clip_name = $2",
            user_id, clip_name,
        )
        await conn.close()

        if row:
            return DatabaseManager._row_to_video_clip(row)
        return None

    @staticmethod
    async def get_clip_by_index(user_id: int, index: int) -> Optional[VideoClip]:
        conn = await DatabaseManager.get_db_connection()
        row = await conn.fetchrow(
            "SELECT id, chat_id, user_id, clip_name, video_data, start_time, end_time, duration, season, episode_number, is_compilation "
            "FROM video_clips "
            "WHERE user_id = $1 "
            "ORDER BY id "
            "LIMIT 1 OFFSET $2",
            user_id, index - 1,
        )
        await conn.close()

        if row:
            return DatabaseManager._row_to_video_clip(row)
        return None

    @staticmethod
    async def get_video_data_by_name(user_id: int, clip_name: str) -> Optional[bytes]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval(
            "SELECT video_data FROM video_clips WHERE user_id = $1 AND clip_name = $2",
            user_id, clip_name,
        )
        await conn.close()
        return result

    @staticmethod
    async def add_subscription(user_id: int, days: int) -> Optional[date]:
        conn = await DatabaseManager.get_db_connection()
        new_end_date = await conn.fetchval(
            "UPDATE user_profiles "
            "SET subscription_end = CURRENT_DATE + $2 * interval '1 day' "
            "WHERE user_id = $1 "
            "RETURNING subscription_end",
            user_id, days,
        )
        await conn.close()
        return new_end_date

    @staticmethod
    async def remove_subscription(user_id: int) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            "UPDATE user_profiles "
            "SET subscription_end = NULL "
            "WHERE user_id = $1",
            user_id,
        )
        await conn.close()

    @staticmethod
    async def get_user_subscription(user_id: int) -> Optional[date]:
        conn = await DatabaseManager.get_db_connection()
        subscription_end = await conn.fetchval("SELECT subscription_end FROM user_profiles WHERE user_id = $1", user_id)
        await conn.close()
        return subscription_end

    @staticmethod
    async def add_report(user_id: int, report: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            "INSERT INTO reports (user_id, report) "
            "VALUES ($1, $2)",
            user_id, report,
        )
        await conn.close()

    @staticmethod
    async def delete_clip(user_id: int, clip_name: str) -> str:
        conn = await DatabaseManager.get_db_connection()
        async with conn.transaction():
            result = await conn.execute(
                "DELETE FROM video_clips "
                "WHERE user_id = $1 AND clip_name = $2",
                user_id, clip_name,
            )
        await conn.close()
        return result

    @staticmethod
    async def is_clip_name_unique(chat_id: int, clip_name: str) -> bool:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchval(
            "SELECT COUNT(*) FROM video_clips WHERE chat_id=$1 AND clip_name=$2",
            chat_id, clip_name,
        )
        await conn.close()
        return result == 0

    @staticmethod
    async def insert_last_search(chat_id: int, quote: str, segments: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            "INSERT INTO search_history (chat_id, quote, segments) "
            "VALUES ($1, $2, $3::jsonb)",
            chat_id, quote, segments,
        )
        await conn.close()

    @staticmethod
    async def get_last_search_by_chat_id(chat_id: int) -> Optional[SearchHistory]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchrow(
            "SELECT id, chat_id, quote, segments "
            "FROM search_history "
            "WHERE chat_id = $1 "
            "ORDER BY id DESC "
            "LIMIT 1",
            chat_id,
        )
        await conn.close()

        if result:
            return SearchHistory(
                id=result["id"],
                chat_id=result["chat_id"],
                quote=result["quote"],
                segments=result["segments"],
            )
        return None

    @staticmethod
    async def update_last_search(search_id: int, new_quote: Optional[str] = None, new_segments: Optional[str] = None) -> None:
        conn = await DatabaseManager.get_db_connection()
        if new_quote:
            await conn.execute(
                "UPDATE search_history "
                "SET quote = $1 "
                "WHERE id = $2",
                new_quote, search_id,
            )
        if new_segments:
            await conn.execute(
                "UPDATE search_history "
                "SET segments = $1::jsonb "
                "WHERE id = $2",
                new_segments, search_id,
            )
        await conn.close()

    @staticmethod
    async def delete_search_by_id(search_id: int) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            "DELETE FROM search_history "
            "WHERE id = $1",
            search_id,
        )
        await conn.close()

    @staticmethod
    async def insert_last_clip(
            chat_id: int,
            segment: dict,
            compiled_clip: Optional[bytes],
            clip_type: ClipType,
            adjusted_start_time: Optional[float],
            adjusted_end_time: Optional[float],
            is_adjusted: bool,
    ) -> None:
        conn = await DatabaseManager.get_db_connection()

        segment_json = json.dumps(segment)

        await conn.execute(
            "INSERT INTO last_clips (chat_id, segment, compiled_clip, type, adjusted_start_time, adjusted_end_time, is_adjusted) "
            "VALUES ($1, $2::jsonb, $3::bytea, $4, $5, $6, $7)",
            chat_id, segment_json, compiled_clip, clip_type.value, adjusted_start_time, adjusted_end_time, is_adjusted,
        )
        await conn.close()

    @staticmethod
    async def get_last_clip_by_chat_id(chat_id: int) -> Optional[LastClip]:
        conn = await DatabaseManager.get_db_connection()
        row = await conn.fetchrow(
            "SELECT id, chat_id, segment, compiled_clip, type AS clip_type, adjusted_start_time, adjusted_end_time, is_adjusted, timestamp "
            "FROM last_clips "
            "WHERE chat_id = $1 "
            "ORDER BY id DESC "
            "LIMIT 1",
            chat_id,
        )
        await conn.close()

        if row:
            return LastClip(
                id=row["id"],
                chat_id=row["chat_id"],
                segment=row["segment"],
                compiled_clip=row["compiled_clip"],
                clip_type=ClipType(row["clip_type"]),
                adjusted_start_time=row["adjusted_start_time"],
                adjusted_end_time=row["adjusted_end_time"],
                is_adjusted=row["is_adjusted"],
                timestamp=row["timestamp"],
            )
        return None

    @staticmethod
    async def update_last_clip(
            clip_id: int, new_segment: Optional[str] = None, new_compiled_clip: Optional[bytes] = None,
            new_type: Optional[str] = None,
    ) -> None:
        conn = await DatabaseManager.get_db_connection()
        if new_segment:
            await conn.execute(
                "UPDATE last_clips "
                "SET segment = $1::jsonb "
                "WHERE id = $2",
                new_segment, clip_id,
            )
        if new_compiled_clip:
            await conn.execute(
                "UPDATE last_clips "
                "SET compiled_clip = $1::bytea "
                "WHERE id = $2",
                new_compiled_clip, clip_id,
            )
        if new_type:
            await conn.execute(
                "UPDATE last_clips "
                "SET type = $1 "
                "WHERE id = $2",
                new_type, clip_id,
            )
        await conn.close()

    @staticmethod
    async def delete_clip_by_id(clip_id: int) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            "DELETE FROM last_clips WHERE id = $1",
            clip_id,
        )
        await conn.close()

    @staticmethod
    async def get_all_user_keys() -> Optional[List[UserMessage]]:
        conn = await DatabaseManager.get_db_connection()
        rows = await conn.fetch(
            "SELECT user_id, key, timestamp FROM user_keys",
        )
        await conn.close()

        return [
            UserMessage(
                user_id=row["user_id"],
                key=row["key"],
                timestamp=row["timestamp"],
            ) for row in rows
        ] if rows else None

    @staticmethod
    async def update_user_note(user_id: int, note: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            "UPDATE user_profiles SET note = $1 WHERE user_id = $2",
            note, user_id,
        )
        await conn.close()

    @staticmethod
    async def log_command_usage(user_id: int) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            "INSERT INTO user_command_limits (user_id, timestamp) VALUES ($1, NOW())",
            user_id,
        )
        await conn.close()

    @staticmethod
    async def is_command_limited(user_id: int, limit: int, duration_seconds: int) -> bool:
        usage_count = await DatabaseManager.get_command_usage_count(user_id, duration_seconds)
        return usage_count >= limit

    @staticmethod
    async def get_command_usage_count(user_id: int, duration_seconds: int) -> int:
        conn = await DatabaseManager.get_db_connection()
        time_threshold = datetime.now() - timedelta(seconds=duration_seconds)
        count = await conn.fetchval(
            "SELECT COUNT(*) FROM user_command_limits WHERE user_id = $1 AND timestamp >= $2",
            user_id, time_threshold,
        )
        await conn.close()
        return count

    @staticmethod
    async def is_admin_or_moderator(user_id: int) -> bool:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchrow(
            "SELECT is_admin, is_moderator "
            "FROM user_roles "
            "WHERE user_id = $1",
            user_id,
        )
        await conn.close()

        if result:
            return result["is_admin"] or result["is_moderator"]
        return False

    @staticmethod
    async def get_subscription_days_by_key(key: str) -> Optional[int]:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.fetchrow(
            "SELECT days FROM subscription_keys WHERE key = $1 AND is_active = TRUE",
            key,
        )
        await conn.close()
        return result['days'] if result else None

    @staticmethod
    async def deactivate_subscription_key(key: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            "UPDATE subscription_keys SET is_active = FALSE WHERE key = $1",
            key,
        )
        await conn.close()

    @staticmethod
    async def create_subscription_key(days: int, key: str) -> None:
        conn = await DatabaseManager.get_db_connection()
        await conn.execute(
            "INSERT INTO subscription_keys (key, days, is_active) VALUES ($1, $2, TRUE)",
            key, days,
        )
        await conn.close()

    @staticmethod
    async def remove_subscription_key(key: str) -> bool:
        conn = await DatabaseManager.get_db_connection()
        result = await conn.execute(
            "DELETE FROM subscription_keys WHERE key = $1",
            key,
        )
        await conn.close()
        return result == "DELETE 1"

    @staticmethod
    async def get_all_subscription_keys() -> List[SubscriptionKey]:
        conn = await DatabaseManager.get_db_connection()
        rows = await conn.fetch("SELECT * FROM subscription_keys")
        await conn.close()
        return [SubscriptionKey(**row) for row in rows]
