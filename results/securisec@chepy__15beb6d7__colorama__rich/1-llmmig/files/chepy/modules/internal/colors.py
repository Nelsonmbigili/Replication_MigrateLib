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
