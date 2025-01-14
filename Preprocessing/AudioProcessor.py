import argparse
from pathlib import Path
import subprocess
import sys
from typing import List

from Preprocessing.ErrorHandlingLogger import ErrorHandlingLogger
from Preprocessing.utils import setup_logger


class AudioProcessor:
    DEFAULT_MODEL: str = "large-v3"
    DEFAULT_LANGUAGE: str = "Polish"
    DEFAULT_DEVICE: str = "cuda"
    SUPPORTED_EXTENSIONS: List[str] = {".wav", ".mp3"}

    def __init__(self, input_folder: str, output_folder: str, model: str, language: str, device: str):
        self.input_folder: Path = Path(input_folder)
        self.output_folder: Path = Path(output_folder)
        self.model: str = model
        self.language: str = language
        self.device: str = device
        self.logger: ErrorHandlingLogger = ErrorHandlingLogger(
            class_name=self.__class__.__name__,
            logger=setup_logger(self.__class__.__name__),
        )

    def run(self) -> int:
        self.logger.info("Starting audio processing...")
        try:
            self.process_folder()
        except Exception as e:
            self.logger.error(f"Unexpected critical error in run: {e}")
        return self.logger.finalize()

    def process_folder(self) -> None:
        try:
            if not self.input_folder.exists() or not self.input_folder.is_dir():
                self.logger.error(f"Invalid input folder path: {self.input_folder}")
                return

            for file_path in self.input_folder.rglob("*"):
                if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                    self.process_audio_file(file_path)
        except Exception as e:
            self.logger.error(f"Unexpected error in process_folder: {e}")

    def process_audio_file(self, file_path: Path) -> None:
        try:
            relative_path = file_path.relative_to(self.input_folder)
            output_path = self.output_folder / relative_path.with_suffix("_processed.wav")
            output_path.parent.mkdir(parents=True, exist_ok=True)

            subprocess.run(
                [
                    "whisper", str(file_path), "--model", self.model, "--language", self.language, "--device", self.device,
                    "--output_dir", str(output_path.parent),
                ],
                check=True,
            )
            self.logger.info(f"Processed: {file_path} -> {output_path}")
        except subprocess.CalledProcessError as e:
            self.logger.error(f"Subprocess error while processing {file_path}: {e}")
        except FileNotFoundError as e:
            self.logger.error(f"Command not found for {file_path}: {e}")
        except PermissionError as e:
            self.logger.error(f"Permission error with file {file_path}: {e}")
        except Exception as e:
            self.logger.error(f"Unexpected error in process_audio_file for {file_path}: {e}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Process .wav and .mp3 files using Whisper model.")
    parser.add_argument("input_folder", type=Path, help="Path to the input folder")
    parser.add_argument("output_folder", type=Path, help="Path to the output folder")
    parser.add_argument("--model", type=str, default=AudioProcessor.DEFAULT_MODEL, help="Whisper model to use")
    parser.add_argument("--language", type=str, default=AudioProcessor.DEFAULT_LANGUAGE, help="Language to use")
    parser.add_argument("--device", type=str, default=AudioProcessor.DEFAULT_DEVICE, help="Device to use")

    args = parser.parse_args()

    processor = AudioProcessor(
        input_folder=args.input_folder,
        output_folder=args.output_folder,
        model=args.model,
        language=args.language,
        device=args.device,
    )
    exit_code = processor.run()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
