import logging
import socket


def _allowed_gai_family_4():
    """Force IPv4 by overriding socket.getaddrinfo."""
    return socket.AF_INET


def _allowed_gai_family_6():
    """Force IPv6 by overriding socket.getaddrinfo."""
    return socket.AF_INET6


def _allowed_gai_family_unspec():
    """Allow both IPv4 and IPv6."""
    return socket.AF_UNSPEC


def enforce_ip_version(version=None):
    """
    Tries to enforce either IPv4 or IPv6, depending on the version parameter
    :param version: The IP version to use
    :return:
    """
    if version is None:
        # Reset to default behavior (allow both IPv4 and IPv6)
        socket.getaddrinfo = socket.__original_getaddrinfo__
        return

    version = str(version)

    if version == "4":
        logging.info("Enforcing IPv4!")
        _patch_socket_getaddrinfo(_allowed_gai_family_4)

    elif version == "6":
        logging.info("Enforcing IPv6!")
        if not socket.has_ipv6:
            raise Exception("Your system can't handle IPv6!")

        _patch_socket_getaddrinfo(_allowed_gai_family_6)

    elif version == "5":
        raise ValueError("Internet Stream Protocol? Really? There is no actual IPv5!")

    else:
        raise ValueError("No valid value specified for 'version' parameter! Please use either 4 or 6")


def _patch_socket_getaddrinfo(allowed_family):
    """
    Patches socket.getaddrinfo to enforce the allowed address family.
    :param allowed_family: The address family to enforce (e.g., socket.AF_INET or socket.AF_INET6)
    """
    def custom_getaddrinfo(host, port, family=0, type=0, proto=0, flags=0):
        return socket.__original_getaddrinfo__(host, port, allowed_family(), type, proto, flags)

    # Save the original getaddrinfo function if not already saved
    if not hasattr(socket, "__original_getaddrinfo__"):
        socket.__original_getaddrinfo__ = socket.getaddrinfo

    # Patch the getaddrinfo function
    socket.getaddrinfo = custom_getaddrinfo
