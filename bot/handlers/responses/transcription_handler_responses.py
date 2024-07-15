from typing import (
    Dict,
    List,
    Union,
)


def get_no_quote_provided_message() -> str:
    return "🔎 Podaj cytat, który chcesz znaleźć. Przykład: /klip Nie szkoda panu tego pięknego gabinetu?"


def get_transcription_response(quote: str, context_segments: List[Dict[str, Union[int, str]]]) -> str:
    response = f"🔍 Transkrypcja dla cytatu: \"{quote}\"\n\n```\n"
    for segment in context_segments:
        response += f"🆔 {segment['id']} - {segment['text']}\n"
    response += "```"
    return response


def get_log_transcription_response_sent_message(quote: str, username: str) -> str:
    return f"Transcription for quote '{quote}' sent to user '{username}'."
