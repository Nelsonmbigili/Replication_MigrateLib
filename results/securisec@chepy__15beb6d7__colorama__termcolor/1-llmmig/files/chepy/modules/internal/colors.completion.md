### Explanation of Changes:
The original code uses the `colorama` library to apply colors to strings. To migrate to the `termcolor` library:
1. **Import Changes**: Removed the `colorama` imports (`Fore`, `Back`) and replaced them with `colored` from `termcolor`.
2. **Color Application**: Replaced the `colorama` syntax (e.g., `Fore.RED + s + Fore.RESET`) with the `colored` function from `termcolor`. The `colored` function takes the string to be colored as the first argument and accepts `color` and `on_color` as keyword arguments for text and background colors, respectively.
3. **Background Colors**: For background colors, `termcolor` uses the `on_color` argument with a prefix `on_` (e.g., `on_yellow` for a yellow background).
4. **TTY Check**: Retained the `sys.stdout.isatty()` check to ensure colors are only applied in a TTY environment.

Below is the modified code:

---

### Modified Code:
```python
import sys
from termcolor import colored


def yellow_background(s: str) -> str:  # pragma: no cover
    """Yellow color string if tty
    
    Args:
        s (str): String to color
    
    Returns:
        str: Colored string
    """
    if sys.stdout.isatty():
        return colored(s, color='black', on_color='on_yellow')
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
        return colored(s, color='red')
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
        return colored(s, color='blue')
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
        return colored(s, color='cyan')
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
        return colored(s, color='green')
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
        return colored(s, color='yellow')
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
        return colored(s, color='magenta')
    else:
        return s
```

---

### Key Notes:
- The `colored` function from `termcolor` is used to apply both text and background colors.
- The `on_color` argument is used for background colors, with the prefix `on_` (e.g., `on_yellow`).
- The `sys.stdout.isatty()` check ensures that colors are only applied in a TTY environment, preserving the original behavior.