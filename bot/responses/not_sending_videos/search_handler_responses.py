from bot.utils.functions import format_segment


def get_invalid_args_count_message() -> str:
    return "🔍 Podaj cytat, który chcesz znaleźć. Przykład: /szukaj geniusz"


def format_search_response(unique_segments_count: int, segments) -> str:
    response = f"🔍 Znaleziono {unique_segments_count} pasujących segmentów:\n"
    segment_lines = []

    for i, segment in enumerate(segments[:5], start=1):
        segment_info = format_segment(segment)
        line = (
            f"{i}️⃣ | 📺 {segment_info.episode_formatted} | 🕒 {segment_info.time_formatted}\n"
            f"   👉  {segment_info.episode_title}"
        )
        segment_lines.append(line)

    response += "```\n" + "\n\n".join(segment_lines) + "\n```"
    return response


def get_log_search_results_sent_message(quote: str, username: str) -> str:
    return f"Search results for quote '{quote}' sent to user '{username}'."
