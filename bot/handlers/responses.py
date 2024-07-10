from datetime import date


def get_subscription_status_response(username: str, subscription_end: date, days_remaining: int) -> str:
    return f"""
✨ **Status Twojej subskrypcji** ✨

👤 **Użytkownik:** {username}
📅 **Data zakończenia:** {subscription_end}
⏳ **Pozostało dni:** {days_remaining}

Dzięki za wsparcie projektu! 🎉
"""
