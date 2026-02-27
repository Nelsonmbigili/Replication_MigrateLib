### Explanation of Changes:
To migrate the code from using the `tqdm` library to the `progressbar2` library, the following changes were made:
1. **Import Replacement**: Replaced the import of `tqdm` with `progressbar` from the `progressbar2` library.
2. **Custom Progress Bar Class**: Replaced the `CustomTqdm` class with a new `CustomProgressBar` class that uses `progressbar2`. This class replicates the functionality of the original `CustomTqdm` class, including logging progress updates at the specified logging level.
3. **Progress Bar Initialization**: Adapted the progress bar initialization and update logic to use `progressbar2`'s API.
4. **Logging Integration**: Ensured that progress updates are logged only if the logger is enabled for the specified level.

### Modified Code:
```python
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
```

### Key Notes:
1. The `CustomProgressBar` class provides a similar interface to the original `CustomTqdm` class, allowing for seamless integration with the rest of the application.
2. The `update` method is used to update the progress bar, and the `finish` method is used to complete it.
3. The `setLevel` method allows the logging level to be dynamically adjusted, just like in the original `CustomTqdm` class.
4. The `progressbar2` library does not have a direct equivalent to `tqdm`'s `display` method, so the `update` method is used to log progress updates conditionally based on the logging level.