import logging
from typing import Dict, Any, Optional
from termcolor import colored


class ColoredFormatter(logging.Formatter):
    """Custom formatter to add colors to log messages based on their level."""

    COLORS: Dict[str, str] = {
        "DEBUG": "blue",
        "INFO": "cyan",
        "WARNING": "yellow",
        "ERROR": "red",
        "CRITICAL": "red",
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format the log record with appropriate colors.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message with color.
        """
        levelname: str = record.levelname
        if levelname in self.COLORS:
            record.levelname = colored(levelname, self.COLORS[levelname], attrs=["bold"] if levelname == "CRITICAL" else None)
        return super().format(record)


class Logger:
    """Custom logger class for RepopackPy."""

    def __init__(self) -> None:
        """Initialize the logger with a console handler and colored formatter."""
        self.logger: logging.Logger = logging.getLogger("repopack-py")
        self.logger.setLevel(logging.INFO)

        console_handler: logging.StreamHandler = logging.StreamHandler()
        console_handler.setFormatter(ColoredFormatter("%(levelname)s: %(message)s"))
        self.logger.addHandler(console_handler)

    def set_verbose(self, verbose: bool) -> None:
        """
        Set the verbosity level of the logger.

        Args:
            verbose (bool): If True, set to DEBUG level; otherwise, set to INFO level.
        """
        self.logger.setLevel(logging.DEBUG if verbose else logging.INFO)

    def debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message."""
        self.logger.debug(message, **kwargs)

    def info(self, message: str, **kwargs: Any) -> None:
        """Log an info message."""
        self.logger.info(message, **kwargs)

    def warning(self, message: str, **kwargs: Any) -> None:
        """Log a warning message."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs: Any) -> None:
        """Log an error message."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs: Any) -> None:
        """Log a critical message."""
        self.logger.critical(message, **kwargs)

    def trace(self, message: str) -> None:
        """
        Log a trace message if the logger level is set to DEBUG or lower.

        Args:
            message (str): The trace message to log.
        """
        if self.logger.level <= logging.DEBUG:
            self.logger.debug(colored(f"TRACE: {message}", "magenta"))


# Create a global logger instance
logger: Logger = Logger()
