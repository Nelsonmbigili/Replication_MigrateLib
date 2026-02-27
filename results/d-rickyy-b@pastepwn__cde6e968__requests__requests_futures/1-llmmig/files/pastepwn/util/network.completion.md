### Explanation of Changes:
The provided code does not directly use the `requests` library for making HTTP requests. Instead, it interacts with `requests.packages.urllib3.util.connection` to modify the behavior of IP version enforcement. Since the migration to `requests_futures` involves asynchronous HTTP requests, and the code provided does not include any HTTP request logic, **no changes are required to migrate this specific code to `requests_futures`**.

The `requests_futures` library is a wrapper around `requests` that provides asynchronous capabilities using `concurrent.futures`. However, the provided code does not make any HTTP requests or use synchronous request methods like `requests.get()` or `requests.post()`. Therefore, the migration does not apply to this code snippet.

### Modified Code:
Since no changes are necessary, the code remains the same:

```python
import logging
import socket

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

### Summary:
The code provided does not involve any HTTP requests or synchronous request methods from the `requests` library. Therefore, no changes are required to migrate this code to use `requests_futures`. If you have additional code that involves HTTP requests, please provide it, and I can assist with the migration.