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
# On créé une classe à utiliser à la place de celle de alive-progress
# def level: INFO
class CustomTqdm:
    level = logging.INFO

    def __init__(self, total=None, **kwargs):
        self.bar = alive_bar(total, **kwargs)

    def display(self, msg=None):
        if logger.isEnabledFor(self.level):
            self.bar.text(msg)

    def close(self):
        if logger.isEnabledFor(self.level):
            self.bar.stop()

    @staticmethod
    def setLevel(level):
        CustomTqdm.level = level
