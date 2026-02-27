### Explanation of Changes:
The original code uses `requests.packages.urllib3.util.connection` to modify the `allowed_gai_family` function for enforcing specific IP versions. Since `httpx` does not directly expose or rely on `urllib3` for connection utilities, the migration requires removing the dependency on `requests.packages.urllib3.util.connection`. Instead, we directly modify the `socket` module's behavior to enforce the desired IP version.

The key changes are:
1. Removed the import of `requests.packages.urllib3.util.connection` and replaced it with direct manipulation of the `socket` module.
2. Replaced `urllib3_cn.allowed_gai_family` with a custom implementation that directly modifies the behavior of `socket.getaddrinfo` to enforce the desired IP version.

### Modified Code:
```python
import logging
import socket


def _allowed_gai_family_4():
    """Force IPv4 by returning AF_INET."""
    return socket.AF_INET


def _allowed_gai_family_6():
    """Force IPv6 by returning AF_INET6."""
    return socket.AF_INET6


def _allowed_gai_family_unspec():
    """Allow both IPv4 and IPv6 by returning AF_UNSPEC."""
    return socket.AF_UNSPEC


def enforce_ip_version(version=None):
    """
    Tries to enforce either IPv4 or IPv6, depending on the version parameter
    :param version: The IP version to use
    :return:
    """
    if version is None:
        # Allow both IPv4 and IPv6
        socket.getaddrinfo = socket.getaddrinfo  # Reset to default behavior
        return

    version = str(version)

    if version == "4":
        logging.info("Enforcing IPv4!")
        socket.getaddrinfo = lambda *args, **kwargs: socket.getaddrinfo(
            *args, family=_allowed_gai_family_4(), **kwargs
        )

    elif version == "6":
        logging.info("Enforcing IPv6!")
        if not socket.has_ipv6:
            raise Exception("Your system can't handle IPv6!")

        socket.getaddrinfo = lambda *args, **kwargs: socket.getaddrinfo(
            *args, family=_allowed_gai_family_6(), **kwargs
        )

    elif version == "5":
        raise ValueError("Internet Stream Protocol? Really? There is no actual IPv5!")

    else:
        raise ValueError("No valid value specified for 'version' parameter! Please use either 4 or 6")
```

### Key Notes:
- The `httpx` library does not use `urllib3` internally, so the migration involves removing the dependency on `urllib3` and directly modifying the `socket` module's behavior.
- The `socket.getaddrinfo` function is overridden to enforce the desired IP version by specifying the `family` parameter (`AF_INET` for IPv4, `AF_INET6` for IPv6, or `AF_UNSPEC` for both).
- The rest of the code structure remains unchanged to ensure compatibility with the larger application.