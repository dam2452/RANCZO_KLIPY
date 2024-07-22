from dataclasses import dataclass
from typing import Optional


@dataclass
class User:
    name: str
    is_admin: Optional[bool]
    is_moderator: Optional[bool]
    full_name: Optional[str]
    email: Optional[str]
    phone: Optional[str]
