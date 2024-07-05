import subprocess
import os
import json
import argparse


def get_best_audio_stream(video_file):
    """Zwraca indeks najlepszej ścieżki audio na podstawie bitrate."""
    try:
        cmd = f'ffprobe -v quiet -print_format json -show_streams -select_streams a "{video_file}"'
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        streams = json.loads(result.stdout)['streams']

        # Upewniamy się, że wartości bitrate są traktowane jako liczby całkowite
        best_stream = max(streams, key=lambda s: int(s.get('bit_rate', 0)))
        return best_stream['index']
    except Exception as e:
        print(f"Błąd podczas wybierania ścieżki audio: {e}")
        return None


def convert_and_normalize_audio(video_file, audio_index, output_audio_file):
    """Konwertuje wybraną ścieżkę audio do formatu WAV, mono, z normalizacją głośności."""
    try:
        # Konwersja do formatu WAV, mono
        cmd = f'ffmpeg -i "{video_file}" -map 0:{audio_index} -acodec pcm_s16le -ar 48000 -ac 1 "{output_audio_file}"'
        subprocess.run(cmd, shell=True, check=True)
        print(f"Przekonwertowano audio: {output_audio_file}")

        # Normalizacja głośności do tymczasowego pliku
        temp_output_audio_file = output_audio_file.replace('.wav', '_normalized.wav')
        normalize_cmd = f'ffmpeg -i "{output_audio_file}" -filter:a "dynaudnorm" "{temp_output_audio_file}"'
        subprocess.run(normalize_cmd, shell=True, check=True)
        print(f"Audio znormalizowane: {temp_output_audio_file}")

        # Zamiana plików
        os.replace(temp_output_audio_file, output_audio_file)
        print(f"Zastąpiono oryginalny plik znormalizowanym audio: {output_audio_file}")

    except subprocess.CalledProcessError as e:
        print(f"Błąd podczas konwersji audio: {e}")


def process_folder(input_folder, output_folder):
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
        description="Przetwarza pliki wideo w podanym folderze, konwertując i normalizując audio do formatu WAV.")
    parser.add_argument("input_folder", type=str, help="Folder wejściowy zawierający pliki wideo.")
    parser.add_argument("output_folder", type=str,
                        help="Folder wyjściowy do zapisywania znormalizowanych plików audio.")

    args = parser.parse_args()

    process_folder(args.input_folder, args.output_folder)
