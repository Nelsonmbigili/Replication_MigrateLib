import logging
import socket
import pycurl


def _allowed_gai_family_4():
    """Placeholder for IPv4 enforcement logic in pycurl"""
    return pycurl.IPRESOLVE_V4


def _allowed_gai_family_6():
    """Placeholder for IPv6 enforcement logic in pycurl"""
    return pycurl.IPRESOLVE_V6


def _allowed_gai_family_unspec():
    """Placeholder for no specific IP version enforcement in pycurl"""
    return pycurl.IPRESOLVE_WHATEVER


def enforce_ip_version(version=None):
    """
    Tries to enforce either IPv4 or IPv6, depending on the version parameter
    :param version: The IP version to use
    :return:
    """
    if version is None:
        logging.info("No specific IP version enforced (default behavior).")
        ip_resolve = _allowed_gai_family_unspec()
        return ip_resolve

    version = str(version)

    if version == "4":
        logging.info("Enforcing IPv4!")
        ip_resolve = _allowed_gai_family_4()
        return ip_resolve

    elif version == "6":
        logging.info("Enforcing IPv6!")
        if not socket.has_ipv6:
            raise Exception("Your system can't handle IPv6!")

        ip_resolve = _allowed_gai_family_6()
        return ip_resolve

    elif version == "5":
        raise ValueError("Internet Stream Protocol? Really? There is no actual IPv5!")

    else:
        raise ValueError("No valid value specified for 'version' parameter! Please use either 4 or 6")
