The following Python code currently uses the library "matplotlib" version 3.9.1.
Migrate this code to use the library "altair" version 5.5.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "matplotlib" to "altair".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "matplotlib" and "altair".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
import pytest
from unittest.mock import patch
from matplotlib.font_manager import FontProperties
from pyfonts import load_font


def test_load_font_with_url():
    font = load_font(
        font_url="https://github.com/JosephBARBIERDARNAL/pyfonts/blob/main/tests/Ultra-Regular.ttf?raw=true"
    )
    assert isinstance(font, FontProperties)


def test_load_font_with_path():
    font = load_font(font_path="tests/Ultra-Regular.ttf")
    assert isinstance(font, FontProperties)


def test_load_font_invalid_input():
    with pytest.raises(ValueError):
        load_font(font_url="http://example.com/font.ttf", font_path="/path/to/font.ttf")


def test_load_font_no_input():
    with pytest.raises(ValueError):
        load_font()

```