### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the primary change involves replacing the synchronous request calls with asynchronous ones provided by `requests_futures`. This allows for non-blocking HTTP requests, which can improve performance in applications that make multiple requests. The `requests_futures` library provides a `FuturesSession` class that extends the standard `requests.Session` to support asynchronous requests.

In the modified code, I will import `FuturesSession` from `requests_futures.sessions` and replace instances of `requests` with `FuturesSession`. However, since the original code does not contain any direct HTTP request calls, the migration will focus on the import and setup of the `FuturesSession`.

### Modified Code
```python
import logging
import socket
from requests_futures.sessions import FuturesSession  # Importing FuturesSession

import requests.packages.urllib3.util.connection as urllib3_cn


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

In this modified code, I have added the import statement for `FuturesSession` from `requests_futures.sessions`. The rest of the code remains unchanged, as there are no direct HTTP requests in the provided snippet. If there were any requests made, they would need to be updated to use `FuturesSession` for asynchronous behavior.