import json
import os

folder_path = 'JSONTEST'

keys_to_remove = ["tokens", "no_speech_prob", "compression_ratio", "avg_logprob", "temperature", "language", "seek"]

def replace_unicode_chars(text):
    """Zamienia kody Unicode na polskie znaki w tekście."""
    unicode_map_reversed = {
        '\\u0105': 'ą', '\\u0107': 'ć', '\\u0119': 'ę', '\\u0142': 'ł',
        '\\u0144': 'ń', '\\u00F3': 'ó', '\\u015B': 'ś', '\\u017A': 'ź',
        '\\u017C': 'ż', '\\u0104': 'Ą', '\\u0106': 'Ć', '\\u0118': 'Ę',
        '\\u0141': 'Ł', '\\u0143': 'Ń', '\\u00D3': 'Ó', '\\u015A': 'Ś',
        '\\u0179': 'Ź', '\\u017B': 'Ż',
    }
    for unicode_char, char in unicode_map_reversed.items():
        text = text.replace(unicode_char, char)
    return text

def process_json_files(folder):
    """Przetwarza wszystkie pliki JSON w folderze, usuwając niechciane klucze i dodając 'author', 'Comment', 'tags', 'location', 'actors'."""
    for filename in os.listdir(folder):
        if filename.endswith('.json'):
            file_path = os.path.join(folder, filename)
            with open(file_path, 'r', encoding='utf-8') as file:
                data = json.load(file)

            if 'segments' in data:
                for segment in data['segments']:
                    for key in keys_to_remove:
                        segment.pop(key, None)
                    segment['text'] = replace_unicode_chars(segment.get('text', ''))
                    segment['author'] = ""
                    segment['comment'] = ""
                    segment['tags'] = ["", ""]
                    segment['location'] = ""
                    segment['actors'] = ["", ""]

            organized_data = {
                'segments': data['segments'],
            }

            with open(file_path, 'w', encoding='utf-8') as file:
                json.dump(organized_data, file, ensure_ascii=False, indent=4)
            print(f'Przetworzono plik: {filename}')

process_json_files(folder_path)
