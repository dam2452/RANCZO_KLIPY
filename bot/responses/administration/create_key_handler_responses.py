
def get_create_key_usage_message() -> str:
    return "❌ Podaj liczbę dni i klucz. Przykład: /addkey 30 tajny_klucz ❌"


def get_create_key_success_message(days: int, key: str) -> str:
    return f"✅ Stworzono klucz: `{key}` na {days} dni. ✅"
