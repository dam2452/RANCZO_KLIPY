from datetime import date
from typing import (
    Dict,
    List,
    Union,
)

import asyncpg
from tabulate import tabulate




















def get_user_updated_message(username: str) -> str:
    return f"✅ Zaktualizowano dane użytkownika {username}.✅"





# fixme  tworzymy nowy folder "responses" i tam robimy np. delete_clip_responses.py dla kazdego handlera + generic wspoldzielone i WSZYSTKIE response'y mamy wyjebane do osobnych plikow i od razu wiadomo co zwraca ktory handler albo co jest wspoldzielone








def get_no_quote_provided_message() -> str:
    return "✏️ Podaj cytat, który chcesz znaleźć.✏️"


def get_no_segments_found_message(quote: str) -> str:
    return f"❌ Nie znaleziono pasujących segmentów dla cytatu: \"{quote}\".❌"









