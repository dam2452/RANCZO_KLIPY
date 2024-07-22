import argparse
import json
import logging
import os
from typing import Optional

import ffmpeg

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_best_audio_stream(video_file: str) -> Optional[int]:
    """Zwraca indeks najlepszej ścieżki audio na podstawie bitrate."""
    try:
        probe = ffmpeg.probe(video_file, select_streams='a', show_streams=True)
        streams = probe['streams']

        # Upewniamy się, że wartości bitrate są traktowane jako liczby całkowite
        best_stream = max(streams, key=lambda s: int(s.get('bit_rate', 0)))
        return best_stream['index']
    except ffmpeg.Error as e:
        logger.error(f"Błąd podczas wybierania ścieżki audio: {e.stderr.decode('utf-8')}")
        return None
    except KeyError as e:
        logger.error(f"Brak klucza w danych wyjściowych: {e}")
        return None
    except json.JSONDecodeError as e:
        logger.error(f"Błąd podczas dekodowania JSON: {e}")
        return None


def convert_and_normalize_audio(video_file: str, audio_index: int, output_audio_file: str) -> None:
    """Konwertuje wybraną ścieżkę audio do formatu WAV, mono, z normalizacją głośności."""
    try:
        # Konwersja do formatu WAV, mono
        temp_output_audio_file = output_audio_file.replace('.wav', '_normalized.wav')
        ffmpeg.input(video_file, **{'map': f'0:{audio_index}'}).output(
            output_audio_file, acodec='pcm_s16le', ar=48000, ac=1,
        ).run()
        logger.info(f"Przekonwertowano audio: {output_audio_file}")

        # Normalizacja głośności do tymczasowego pliku
        ffmpeg.input(output_audio_file).output(
            temp_output_audio_file, filter='dynaudnorm',
        ).run()
        logger.info(f"Audio znormalizowane: {temp_output_audio_file}")

        os.replace(temp_output_audio_file, output_audio_file)
        logger.info(f"Zastąpiono oryginalny plik znormalizowanym audio: {output_audio_file}")

    except ffmpeg.Error as e:
        logger.error(f"Błąd podczas konwersji audio: {e.stderr.decode('utf-8')}")
    except OSError as e:
        logger.error(f"Błąd operacji plikowych: {e}")


def process_folder(input_folder: str, output_folder: str) -> None:
    """Przetwarza wszystkie pliki wideo w podanym folderze, zachowując strukturę folderów."""
    for root, _, files in os.walk(input_folder):
        for file in files:
            if file.lower().endswith(('.mp4', '.mkv', '.avi')):
                video_path = os.path.join(root, file)
                relative_path = os.path.relpath(root, input_folder)
                target_folder = os.path.join(output_folder, relative_path)
                os.makedirs(target_folder, exist_ok=True)

                audio_index = get_best_audio_stream(video_path)
                if audio_index is not None:
                    output_audio_file = os.path.join(target_folder, os.path.splitext(file)[0] + '.wav')
                    convert_and_normalize_audio(video_path, audio_index, output_audio_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Przetwarza pliki wideo w podanym folderze, konwertując i normalizując audio do formatu WAV.",
    )
    parser.add_argument("input_folder", type=str, help="Folder wejściowy zawierający pliki wideo.")
    parser.add_argument(
        "output_folder", type=str,
        help="Folder wyjściowy do zapisywania znormalizowanych plików audio.",
    )

    args = parser.parse_args()

    process_folder(args.input_folder, args.output_folder)
