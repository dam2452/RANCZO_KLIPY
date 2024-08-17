from typing import (
    List,
    Optional,
)

from bot.database.user import User


class InvalidTimeStringException(Exception):
    def __init__(self, time: str) -> None:
        self.message = f"Invalid time string: '{time}'"
        super().__init__(self.message)


def minutes_str_to_seconds(time_str: str) -> float:
    try:
        minutes, seconds = time_str.split(':')
        seconds, milliseconds = seconds.split('.')
        total_seconds = int(minutes) * 60 + int(seconds) + int(milliseconds) / 1000
        return total_seconds
    except (TypeError, ValueError) as e:
        raise InvalidTimeStringException from e


def convert_seconds_to_time_str(seconds: int) -> str:
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


def time_str_to_seconds(time_str: str) -> int:
    h, m, s = [int(part) for part in time_str.split(':')]
    return h * 3600 + m * 60 + s


def parse_whitelist_message(content: List[str], default_admin_status: Optional[bool], default_moderator_status: Optional[bool]) -> User:
    return User(
        name=content[1],
        is_admin=bool(int(content[2])) if len(content) > 2 else default_admin_status,
        is_moderator=bool(int(content[3])) if len(content) > 3 else default_moderator_status,
        full_name=content[4] if len(content) > 4 else None,
        email=content[5] if len(content) > 5 else None,
        phone=content[6] if len(content) > 6 else None,
    )
