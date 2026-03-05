### Explanation of Changes
To migrate the code from using the `requests` library to using `urllib3`, the following changes were made:

1. **Import Statement**: The import statement for `urllib3` was updated to directly import from `urllib3` instead of `requests.packages.urllib3`.
2. **Accessing `allowed_gai_family` and `HAS_IPV6`**: The attributes `allowed_gai_family` and `HAS_IPV6` were accessed directly from `urllib3.util.connection` instead of through `requests.packages.urllib3.util.connection`.

These changes ensure that the code now utilizes `urllib3` directly, adhering to the new library structure.

### Modified Code
```python
import logging
import socket

import urllib3.util.connection as urllib3_cn


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
        urllib3_cn.allowed_gai_family = _allowed_gai_family_unspec
        return

    version = str(version)

    if version == "4":
        logging.info("Enforcing IPv4!")
        urllib3_cn.allowed_gai_family = _allowed_gai_family_4

    elif version == "6":
        logging.info("Enforcing IPv6!")
        if not urllib3_cn.HAS_IPV6:
            raise Exception("Your system can't handle IPv6!")

        urllib3_cn.allowed_gai_family = _allowed_gai_family_6

    elif version == "5":
        raise ValueError("Internet Stream Protocol? Really? There is no actual IPv5!")

    else:
        raise ValueError("No valid value specified for 'version' parameter! Please use either 4 or 6")
```