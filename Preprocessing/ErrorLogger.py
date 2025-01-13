class ErrorLogger:
    def __init__(self, logger):
        self.logger = logger
        self.errors = []

    def log_error(self, message: str) -> None:
        self.logger.error(message)
        self.errors.append(message)

    def finalize(self) -> int:
        if self.errors:
            self.logger.error("Processing completed with errors:")
            for error in self.errors:
                self.logger.error(f"- {error}")
            return 1
        self.logger.info("Processing completed successfully.")
        return 0
