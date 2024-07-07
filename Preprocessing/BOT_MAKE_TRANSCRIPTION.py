import argparse
import os
import subprocess


def przetworz_folder(folder_wejsciowy: str, folder_wyjsciowy: str) -> None:
    model = "large-v3"
    jezyk = "Polish"
    urzadzenie = "cuda"

    for sciezka_katalogu, _, lista_plikow in os.walk(folder_wejsciowy):
        for plik in lista_plikow:
            if plik.endswith(('.wav', '.mp3')):
                sciezka_wejsciowa = os.path.join(sciezka_katalogu, plik)
                nazwa_pliku_wyjsciowego = plik.split('.')[0] + '_przetworzone.wav'
                sciezka_wyjsciowa = os.path.join(
                    folder_wyjsciowy, os.path.relpath(sciezka_katalogu, folder_wejsciowy),
                    nazwa_pliku_wyjsciowego,
                )

                if not os.path.exists(os.path.dirname(sciezka_wyjsciowa)):
                    os.makedirs(os.path.dirname(sciezka_wyjsciowa))

                subprocess.run(
                    [
                        "whisper", sciezka_wejsciowa, "--model", model, "--language", jezyk, "--device", urzadzenie,
                        "--output_dir", folder_wyjsciowy,
                    ], check=True,
                )


def main() -> None:
    parser = argparse.ArgumentParser(description='Przetwarzanie plików .wav i .mp3 za pomocą modelu whisper')
    parser.add_argument('folder_wejsciowy', type=str, help='Ścieżka do folderu wejściowego')
    parser.add_argument('folder_wyjsciowy', type=str, help='Ścieżka do folderu wyjściowego')

    args = parser.parse_args()

    przetworz_folder(args.folder_wejsciowy, args.folder_wyjsciowy)


if __name__ == '__main__':
    main()
