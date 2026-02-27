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
