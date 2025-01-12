import argparse
import logging
from pathlib import Path
import subprocess


class AudioProcessor:
    DEFAULT_MODEL = "large-v3"
    DEFAULT_LANGUAGE = "Polish"
    DEFAULT_DEVICE = "cuda"
    SUPPORTED_EXTENSIONS = {".wav", ".mp3"}

    def __init__(self, input_folder: str, output_folder: str, model: str = None, language: str = None, device: str = None):
        self.input_folder = Path(input_folder)
        self.output_folder = Path(output_folder)
        self.model = model or self.DEFAULT_MODEL
        self.language = language or self.DEFAULT_LANGUAGE
        self.device = device or self.DEFAULT_DEVICE
        self.logger = self.setup_logger()

    # pylint: disable=duplicate-code
    @staticmethod
    def setup_logger() -> logging.Logger:
        logger = logging.getLogger("AudioProcessor")
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    # pylint: enable=duplicate-code
    def process_audio_file(self, file_path: Path) -> None:
        relative_path = file_path.relative_to(self.input_folder)
        output_path = self.output_folder / relative_path.with_suffix("_processed.wav")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        try:
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

    def process_folder(self) -> None:
        if not self.input_folder.exists() or not self.input_folder.is_dir():
            self.logger.error(f"Invalid input folder path: {self.input_folder}")
            raise ValueError(f"Invalid input folder path: {self.input_folder}")

        for file_path in self.input_folder.rglob("*"):
            if file_path.suffix.lower() in self.SUPPORTED_EXTENSIONS:
                self.process_audio_file(file_path)

    def run(self) -> None:
        self.logger.info("Starting audio processing...")
        self.process_folder()
        self.logger.info("Audio processing completed.")


def main() -> None:
    parser = argparse.ArgumentParser(description="Process .wav and .mp3 files using Whisper model.")
    parser.add_argument("input_folder", type=str, help="Path to the input folder")
    parser.add_argument("output_folder", type=str, help="Path to the output folder")
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
    processor.run()


if __name__ == "__main__":
    main()
