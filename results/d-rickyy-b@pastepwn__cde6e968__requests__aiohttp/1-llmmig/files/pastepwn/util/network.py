import logging
import socket
from contextlib import contextmanager


def _allowed_gai_family_4():
    """Force IPv4."""
    return socket.AF_INET


def _allowed_gai_family_6():
    """Force IPv6."""
    return socket.AF_INET6


def _allowed_gai_family_unspec():
    """Allow both IPv4 and IPv6."""
    return socket.AF_UNSPEC


@contextmanager
def enforce_ip_version(version=None):
    """
    Context manager to enforce either IPv4 or IPv6 for aiohttp operations.
    :param version: The IP version to use (4, 6, or None for both)
    """
    original_getaddrinfo = socket.getaddrinfo

    def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        if family == socket.AF_UNSPEC:
            if version == "4":
                family = _allowed_gai_family_4()
            elif version == "6":
                family = _allowed_gai_family_6()
        return original_getaddrinfo(host, port, family, type, proto, flags)

    if version is None:
        logging.info("Allowing both IPv4 and IPv6!")
    else:
        version = str(version)
        if version == "4":
            logging.info("Enforcing IPv4!")
        elif version == "6":
            logging.info("Enforcing IPv6!")
            if not socket.has_ipv6:
                raise Exception("Your system can't handle IPv6!")
        elif version == "5":
            raise ValueError("Internet Stream Protocol? Really? There is no actual IPv5!")
        else:
            raise ValueError("No valid value specified for 'version' parameter! Please use either 4 or 6")

    # Override socket.getaddrinfo
    socket.getaddrinfo = custom_getaddrinfo
    try:
        yield
    finally:
        # Restore the original getaddrinfo
        socket.getaddrinfo = original_getaddrinfo
