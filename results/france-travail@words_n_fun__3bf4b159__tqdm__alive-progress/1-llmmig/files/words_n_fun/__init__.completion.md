### Explanation of Changes:
To migrate the code from using `tqdm` to `alive-progress`, the following changes were made:
1. Replaced the import of `tqdm` with the import of `alive-progress`'s `alive_bar`.
2. Removed the `CustomTqdm` class, as `alive-progress` does not require subclassing for customization.
3. Replaced the `tqdm`-specific methods (`display`, `close`, etc.) with the equivalent functionality provided by `alive-progress`.
4. Since `alive-progress` does not directly integrate with logging in the same way as `tqdm`, the logging behavior was adjusted to ensure compatibility.

Below is the modified code:

---

### Modified Code:
```python
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
```

---

### Key Notes:
1. The `CustomTqdm` class was replaced with a `CustomAliveBar` class that wraps the `alive_bar` context manager. This ensures that the progress bar is only displayed when the logger's level is appropriate.
2. The `alive_bar` context manager is used to handle the progress bar lifecycle (`__enter__` and `__exit__`).
3. The `setLevel` method was retained to allow dynamic adjustment of the logging level, similar to the original `CustomTqdm` class.
4. The `alive-progress` library does not have a direct equivalent to `tqdm`'s `display` method, so the progress bar is simply managed through the context manager.

This approach ensures minimal disruption to the existing code while successfully migrating to `alive-progress`.