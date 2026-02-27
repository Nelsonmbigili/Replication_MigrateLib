The following Python code currently uses the library "matplotlib" version 3.9.1.
Migrate this code to use the library "seaborn" version 0.13.2 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "matplotlib" to "seaborn".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "matplotlib" and "seaborn".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from .main import load_font
import matplotlib.pyplot as plt
from typing import Optional


def preview_font(
    font_url: Optional[str] = None,
    font_path: Optional[str] = None,
):
    """
    Preview a font.
    """
    font = load_font(font_url, font_path)

    plt.figure(figsize=(10, 5))
    plt.text(
        0.5,
        0.5,
        "Hello, World From PyFonts!",
        fontsize=30,
        ha="center",
        va="center",
        font=font,
    )
    plt.text(
        0.5,
        0.35,
        "This is a test.",
        fontsize=25,
        ha="center",
        va="center",
        font=font,
    )
    plt.text(
        0.5,
        0.65,
        "How about this?",
        fontsize=20,
        ha="center",
        va="center",
        font=font,
    )

    plt.axis("off")
    plt.show()

```