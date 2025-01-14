import logging
from typing import (
    Dict,
    List,
)


class LoggerNotFinalizedException(Exception):

    def __init__(self, errors: List[str]) -> None:
        super().__init__("Logger destroyed without finalize() being called.")
        self.errors: List[str] = errors


class ErrorHandlingLogger:

    CLASS_EXIT_CODES: Dict[str, int] = {
        "AudioNormalizer": 1,
        "AudioProcessor": 2,
        "JSONProcessor": 3,
        "EpisodeInfoProcessor": 4,
        "VideoConverter": 5,
    }

    def __init__(self, logger: logging.Logger, class_name: str) -> None:
        self.logger: logger = logger
        self.class_name: str = class_name

        if class_name not in self.CLASS_EXIT_CODES:
            raise ValueError(f"Class name '{class_name}' not found in CLASS_EXIT_CODES mapping.")

        self.error_exit_code: int = self.CLASS_EXIT_CODES[class_name]
        self.errors: List[str] = []
        self.__is_finalized: bool = False

    def __del__(self) -> None:
        if not self.__is_finalized:
            self.logger.error(f"ErrorHandlingLogger for '{self.class_name}' destroyed without finalize().")
            if self.errors:
                self.logger.error("Logged errors:")
                for error in self.errors:
                    self.logger.error(f"- {error}")
            raise LoggerNotFinalizedException(self.errors)

    def info(self, message: str) -> None:
        self.logger.info(message)

    def error(self, message: str) -> None:
        self.logger.error(message)
        self.errors.append(message)

    def finalize(self) -> int:
        self.__is_finalized = True
        if self.errors:
            self.logger.error(f"Processing for '{self.class_name}' completed with errors:")
            for error in self.errors:
                self.logger.error(f"- {error}")
            return self.error_exit_code
        self.logger.info(f"Processing for '{self.class_name}' completed successfully.")
        return 0
