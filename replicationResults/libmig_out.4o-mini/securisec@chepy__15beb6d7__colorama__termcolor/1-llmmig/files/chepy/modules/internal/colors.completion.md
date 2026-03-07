### Explanation of Changes
To migrate the code from using the `colorama` library to the `termcolor` library, the following changes were made:
1. The import statement was updated to import `colored` from `termcolor` instead of `Fore` and `Back` from `colorama`.
2. The color formatting was changed to use the `colored` function from `termcolor`, which allows specifying both the text color and the background color in a single call.
3. The background color for the `yellow_background` function was adjusted to use the `on_yellow` parameter in the `colored` function.

### Modified Code
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
        return colored(s, 'black', 'on_yellow')
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
        return colored(s, 'red')
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
        return colored(s, 'blue')
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
        return colored(s, 'cyan')
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
        return colored(s, 'green')
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
        return colored(s, 'yellow')
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
        return colored(s, 'magenta')
    else:
        return s
```