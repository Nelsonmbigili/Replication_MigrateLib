import logging
from typing import Dict, Any, Optional
from rich.logging import RichHandler
from rich.text import Text


class Logger:
    """Custom logger class for RepopackPy."""

    def __init__(self) -> None:
        """Initialize the logger with a console handler and rich formatter."""
        self.logger: logging.Logger = logging.getLogger("repopack-py")
        self.logger.setLevel(logging.INFO)

        # Use RichHandler for colored logging
        console_handler: RichHandler = RichHandler(rich_tracebacks=True)
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
            trace_message = Text(f"TRACE: {message}", style="magenta")
            self.logger.debug(trace_message)


# Create a global logger instance
logger: Logger = Logger()
