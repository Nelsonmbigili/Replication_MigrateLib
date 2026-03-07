### Explanation of Changes
To migrate the code from using the `colorama` library to the `rich` library, the following changes were made:

1. **Import Statements**: The import statement was changed from `from colorama import Fore, Back` to `from rich import print`.
2. **Color Formatting**: The color formatting was updated to use the `rich` library's `print` function, which allows for inline styling using the `style` parameter. The `Back` and `Fore` attributes from `colorama` were replaced with the appropriate `rich` syntax for background and foreground colors.
3. **Conditional Output**: The check for whether the output is a TTY (`sys.stdout.isatty()`) was retained, but the way strings are constructed for colored output was modified to use `rich`'s capabilities.

Here is the modified code:

```python
import sys
from rich import print


def yellow_background(s: str) -> str:  # pragma: no cover
    """Yellow color string if tty
    
    Args:
        s (str): String to color
    
    Returns:
        str: Colored string
    """
    if sys.stdout.isatty():
        return f"[black on yellow]{s}[/]"
    else:
        return s


def red(s: str) -> str:  # pragma: no cover
    """Red color string if tty
    
    Args:
        s (str): String to color
    
    Returns:
        str: Colored string

    Examples:
        >>> from chepy.modules.internal.colors import red
        >>> print(RED("some string"))
    """
    if sys.stdout.isatty():
        return f"[red]{s}[/]"
    else:
        return s


def blue(s: str) -> str:  # pragma: no cover
    """Blue color string if tty
    
    Args:
        s (str): String to color
    
    Returns:
        str: Colored string

    Examples:
        >>> from chepy.modules.internal.colors import blue
        >>> print(BLUE("some string"))
    """
    if sys.stdout.isatty():
        return f"[blue]{s}[/]"
    else:
        return s


def cyan(s: str) -> str:  # pragma: no cover
    """Cyan color string if tty
    
    Args:
        s (str): String to color
    
    Returns:
        str: Colored string

    Examples:
        >>> from chepy.modules.internal.colors import cyan
        >>> print(CYAN("some string"))
    """
    if sys.stdout.isatty():
        return f"[cyan]{s}[/]"
    else:
        return s


def green(s: str) -> str:  # pragma: no cover
    """Green color string if tty
    
    Args:
        s (str): String to color
    
    Returns:
        str: Colored string

    Examples:
        >>> from chepy.modules.internal.colors import green
        >>> print(GREEN("some string"))
    """
    if sys.stdout.isatty():
        return f"[green]{s}[/]"
    else:
        return s


def yellow(s: str) -> str:  # pragma: no cover
    """Yellow color string if tty
    
    Args:
        s (str): String to color
    
    Returns:
        str: Colored string

    Examples:
        >>> from chepy.modules.internal.colors import yellow
        >>> print(YELLOW("some string"))
    """
    if sys.stdout.isatty():
        return f"[yellow]{s}[/]"
    else:
        return s


def magenta(s: str) -> str:  # pragma: no cover
    """Magenta color string if tty
    
    Args:
        s (str): String to color
    
    Returns:
        str: Colored string

    Examples:
        >>> from chepy.modules.internal.colors import magenta
        >>> print(MAGENTA("some string"))
    """
    if sys.stdout.isatty():
        return f"[magenta]{s}[/]"
    else:
        return s
```