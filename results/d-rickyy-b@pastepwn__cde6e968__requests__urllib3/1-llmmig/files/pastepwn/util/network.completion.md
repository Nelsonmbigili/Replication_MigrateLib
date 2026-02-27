### Explanation of Changes:
The original code uses `requests.packages.urllib3.util.connection` to access `allowed_gai_family` and `HAS_IPV6`. Since we are migrating to `urllib3` version 2.4.0, we need to directly import these utilities from `urllib3.util.connection` instead of accessing them through the `requests` package. The rest of the code remains unchanged as it is compatible with `urllib3`.

### Modified Code:
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

### Summary of Changes:
1. Replaced `requests.packages.urllib3.util.connection` with `urllib3.util.connection` for importing `allowed_gai_family` and `HAS_IPV6`.
2. No other changes were made to the code, ensuring compatibility with the rest of the application.