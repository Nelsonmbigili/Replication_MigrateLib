### Explanation of Changes
To migrate from the `tqdm` library to the `progressbar2` library, the following changes were made:

1. **Import Statement**: The import statement for `tqdm` was replaced with the import statement for `progressbar2`.
2. **Class Inheritance**: The `CustomTqdm` class now inherits from `progressbar.ProgressBar` instead of `tqdm`.
3. **Method Adjustments**: The `display` and `close` methods were modified to use the appropriate methods from `progressbar2`. The `progressbar` library does not have a `display` method, so it was removed. The `finish` method is used instead of `close` to finalize the progress bar.
4. **Initialization Parameters**: The parameters passed to the `super()` constructor were adjusted to fit the `progressbar2` initialization.

Here is the modified code:

```python
#!/usr/bin/env python3
import logging

from progressbar import ProgressBar

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
# On créé une classe à utiliser à la place de celle de progressbar2
# def level: INFO
class CustomTqdm(ProgressBar):
    level = logging.INFO

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def finish(self):
        if logger.isEnabledFor(self.level):
            super().finish()

    @staticmethod
    def setLevel(level):
        CustomTqdm.level = level
```