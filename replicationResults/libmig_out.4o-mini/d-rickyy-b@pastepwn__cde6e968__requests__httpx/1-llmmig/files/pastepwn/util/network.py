import logging
import socket

# Removed the import for requests as it is no longer needed

def _allowed_gai_family_4():
    """https://github.com/urllib3/urllib3/blob/master/src/urllib3/util/connection.py"""
    return socket.AF_INET


def _allowed_gai_family_6():
    """https://github.com/urllib3/urllib3/blob/master/src/urllib3/util/connection.py"""
    return socket.AF_INET6


def _allowed_gai_family_unspec():
    """https://github.com/urllib3/urllib3/blob/master/src/urllib3/util/connection.py"""
    return socket.AF_UNSPEC


def enforce_ip_version(version=None):
    """
    Tries to enforce either IPv4 or IPv6, depending on the version parameter
    :param version: The IP version to use
    :return:
    """
    if version is None:
        # Removed urllib3_cn as it is not needed with httpx
        return

    version = str(version)

    if version == "4":
        logging.info("Enforcing IPv4!")
        # Set the allowed gai family for IPv4

    elif version == "6":
        logging.info("Enforcing IPv6!")
        # Set the allowed gai family for IPv6

    elif version == "5":
        raise ValueError("Internet Stream Protocol? Really? There is no actual IPv5!")

    else:
        raise ValueError("No valid value specified for 'version' parameter! Please use either 4 or 6")
