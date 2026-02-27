#!/usr/bin/env python3
import logging

from alive_progress import alive_bar

# Get logger (def level: INFO)
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

# Get console handler
# On log tout ce qui est possible ici (i.e >= level du logger)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

# Manage formatter
formatter = logging.Formatter(
    "[%(asctime)s] - %(name)s.%(funcName)s() - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
ch.setFormatter(formatter)

# Add handler to the logger
logger.addHandler(ch)


## Manage alive-progress
# Replace the CustomTqdm class with alive_bar usage
class CustomAliveBar:
    level = logging.INFO

    def __init__(self, total=None, **kwargs):
        self.total = total
        self.bar = None
        self.kwargs = kwargs

    def __enter__(self):
        if logger.isEnabledFor(self.level):
            self.bar = alive_bar(self.total, **self.kwargs)
            return self.bar.__enter__()
        return None

    def __exit__(self, exc_type, exc_value, traceback):
        if self.bar:
            self.bar.__exit__(exc_type, exc_value, traceback)

    @staticmethod
    def setLevel(level):
        CustomAliveBar.level = level
