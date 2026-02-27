#!/usr/bin/env python3
import logging

import progressbar

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


## Manage progressbar2
# Create a custom class to use in place of tqdm
# def level: INFO
class CustomProgressBar:
    level = logging.INFO

    def __init__(self, max_value=None, **kwargs):
        self.max_value = max_value
        self.bar = progressbar.ProgressBar(max_value=max_value, **kwargs)
        self.current_value = 0

    def update(self, value):
        if logger.isEnabledFor(self.level):
            self.current_value = value
            self.bar.update(value)

    def finish(self):
        if logger.isEnabledFor(self.level):
            self.bar.finish()

    @staticmethod
    def setLevel(level):
        CustomProgressBar.level = level
