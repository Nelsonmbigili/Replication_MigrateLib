The following Python code currently uses the library "tqdm" version 4.66.1.
Migrate this code to use the library "progressbar2" version 4.5.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "tqdm" to "progressbar2".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "tqdm" and "progressbar2".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
#!/usr/bin/env python3
import logging

from tqdm import tqdm

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


## Manage tqdm
# On créé une classe à utiliser à la place de celle de tqdm
# def level: INFO
class CustomTqdm(tqdm):
    level = logging.INFO

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def display(self, msg=None, pos=None):
        if logger.isEnabledFor(self.level):
            super().display(msg=msg, pos=pos)

    def close(self):
        if logger.isEnabledFor(self.level):
            super().close()

    @staticmethod
    def setLevel(level):
        CustomTqdm.level = level

```