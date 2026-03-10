### Explanation of Changes
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was removed, as `treq` will be used instead.
2. **Functionality**: The code does not directly use any `requests` functionality, so no changes were needed in the logic of the functions. However, if there were any HTTP requests in the original code, they would need to be replaced with `treq` equivalents.
3. **No Direct Usage of Requests**: Since the provided code does not contain any HTTP requests, the migration primarily involves changing the import statement.

Here is the modified code:

```python
import logging
import socket

import treq  # Changed from requests to treq


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

In this modified code, the only change made was the import statement, reflecting the switch from `requests` to `treq`. The rest of the code remains unchanged, as it does not utilize any HTTP request functionality that would require further modification.