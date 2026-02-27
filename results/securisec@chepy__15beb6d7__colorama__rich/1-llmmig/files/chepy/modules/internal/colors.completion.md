### Explanation of Changes
The migration from `colorama` to `rich` involves replacing the `colorama`-specific methods for applying colors (`Fore`, `Back`, and their respective `RESET` attributes) with `rich`'s `Text` class and its associated styling capabilities. The `rich` library provides a more modern and flexible way to style text using markup or style strings.

Key changes:
1. **Import Replacement**: Removed the `colorama` imports (`Fore`, `Back`) and replaced them with `Text` from `rich.text`.
2. **Color Application**: Replaced the `colorama`-style concatenation of color codes with `Text` objects styled using the `style` parameter.
3. **TTY Check**: Retained the `sys.stdout.isatty()` check to ensure colors are only applied in a TTY environment, as `rich` also supports plain text output when not in a TTY.
4. **Reset Handling**: `rich` automatically handles text styling without requiring explicit reset codes, so no manual resets are needed.

### Modified Code
```python
import sys
from rich.text import Text


def yellow_background(s: str) -> str:  # pragma: no cover
    """Yellow color string if tty
    
    Args:
        s (str): String to color
    
    Returns:
        str: Colored string
    """
    if sys.stdout.isatty():
        return str(Text(s, style="black on yellow"))
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
        return str(Text(s, style="red"))
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
        return str(Text(s, style="blue"))
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
        return str(Text(s, style="cyan"))
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
        return str(Text(s, style="green"))
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
        return str(Text(s, style="yellow"))
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
        return str(Text(s, style="magenta"))
    else:
        return s
```

### Summary of Changes
- Replaced `colorama` imports with `rich.text.Text`.
- Used `Text` objects with the `style` parameter to apply colors and backgrounds.
- Retained the `sys.stdout.isatty()` check to ensure compatibility with non-TTY environments.
- Removed explicit reset codes, as `rich` handles styling automatically.