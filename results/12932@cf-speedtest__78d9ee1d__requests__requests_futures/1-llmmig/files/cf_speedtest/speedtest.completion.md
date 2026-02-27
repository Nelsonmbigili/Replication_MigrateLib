### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures`.
2. **Session Replacement**: Replaced `requests.Session()` with `requests_futures.sessions.FuturesSession()`. This allows asynchronous requests using the `requests_futures` library.
3. **Handling Futures**: Since `requests_futures` returns a `Future` object for asynchronous requests, the `.result()` method is used to block and retrieve the actual response where necessary.
4. **No Other Changes**: The rest of the code remains unchanged, as the migration only affects how requests are made and handled.

---

### Modified Code:
```python
#! /usr/bin/env python3
from __future__ import annotations

import argparse
import math
import statistics
import time
from timeit import default_timer as timer

from requests_futures.sessions import FuturesSession
import urllib3

import cf_speedtest.locations as locations
import cf_speedtest.options as options

REQ_SESSION = FuturesSession()

CGI_ENDPOINT = 'https://speed.cloudflare.com/cdn-cgi/trace'
DOWNLOAD_ENDPOINT = 'https://speed.cloudflare.com/__down?measId=0&bytes={}'
UPLOAD_ENDPOINT = 'https://speed.cloudflare.com/__up?measId=0'

UPLOAD_HEADERS = {
    'Connection': 'keep-alive',
    'DNT': '1',
    'Content-Type': 'text/plain;charset=UTF-8',
    'Accept': '*/*',
}

PROXY_DICT = None
VERIFY_SSL = True
OUTPUT_FILE = None

# Could use python's statistics library, but quantiles are only available
# in version 3.8 and above


def percentile(data: list, percentile: int) -> float:
    size = len(data)
    if percentile == 0:
        return min(data)
    return sorted(data)[int(math.ceil((size * percentile) / 100)) - 1]

# returns ms of how long cloudflare took to process the request, this is in the Server-Timing header


def get_server_timing(server_timing: str) -> float:
    for part in server_timing.split(';'):
        if 'dur=' in part:
            try:
                return float(part.split('=')[1]) / 1000
            except (IndexError, ValueError):
                try:
                    return float(part.split(',')[0].split('=')[1]) / 1000
                except (IndexError, ValueError):
                    pass
    return 0.0

# given an amount of bytes, upload it and return the elapsed seconds taken


def upload_test(total_bytes: int) -> int | float:
    start = timer()

    future = REQ_SESSION.post(
        UPLOAD_ENDPOINT, data=bytearray(
            total_bytes,
        ), headers=UPLOAD_HEADERS, verify=VERIFY_SSL, proxies=PROXY_DICT,
    )
    r = future.result()  # Block and get the response
    r.raise_for_status()
    total_time_taken = timer() - start

    # trust what the server says as time taken
    server_time_taken = get_server_timing(r.headers['Server-Timing'])

    if OUTPUT_FILE:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as datafile:
            datafile.write(
                f'{time.time()},up,{total_bytes},{total_time_taken},{server_time_taken}\n',
            )

    return total_bytes, server_time_taken

# given an amount of bytes, download it and return the elapsed seconds taken


def download_test(total_bytes: int) -> int | float:
    endpoint = DOWNLOAD_ENDPOINT.format(total_bytes)
    start = timer()

    future = REQ_SESSION.get(endpoint, verify=VERIFY_SSL, proxies=PROXY_DICT)
    r = future.result()  # Block and get the response
    r.raise_for_status()

    total_time_taken = timer() - start

    content_size = len(r.content)
    server_time_taken = get_server_timing(r.headers['Server-Timing'])

    if OUTPUT_FILE:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as datafile:
            datafile.write(
                f'{time.time()},down,{content_size},{total_time_taken},{server_time_taken}\n',
            )

    return content_size, total_time_taken - server_time_taken

# calculates http "latency" by measuring download of an empty payload


def latency_test() -> float:
    endpoint = DOWNLOAD_ENDPOINT.format(0)

    start = timer()
    future = REQ_SESSION.get(endpoint, verify=VERIFY_SSL,  proxies=PROXY_DICT)
    r = future.result()  # Block and get the response
    r.raise_for_status()

    total_time_taken = timer() - start
    server_time_taken = get_server_timing(r.headers['Server-Timing'])

    if OUTPUT_FILE:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as datafile:
            datafile.write(
                f'{time.time()},down,{len(r.content)},{total_time_taken},{server_time_taken}\n',
            )

    return total_time_taken - server_time_taken

# See https://speed.cloudflare.com/cdn-cgi/trace


def get_our_country() -> str:
    future = REQ_SESSION.get(CGI_ENDPOINT, verify=VERIFY_SSL,  proxies=PROXY_DICT)
    r = future.result()  # Block and get the response
    r.raise_for_status()

    cgi_data = r.text
    cgi_dict = {
        k: v for k, v in [
            line.split(
                '=',
            ) for line in cgi_data.splitlines()
        ]
    }

    return cgi_dict.get('loc') or 'Unknown'


def preamble() -> str:
    future = REQ_SESSION.get(
        DOWNLOAD_ENDPOINT.format(
            0,
        ), verify=VERIFY_SSL,  proxies=PROXY_DICT,
    )
    r = future.result()  # Block and get the response
    r.raise_for_status()

    our_ip = r.headers.get('cf-meta-ip')
    colo = r.headers.get('cf-meta-colo')
    server_city = colo
    server_country = next(
        (
            loc.get(
                'cca2',
            ) or 'Unknown' for loc in locations.SERVER_LOCATIONS if loc['iata'] == colo.upper()
        ), 'Unknown',
    )
    preamble_str = f'Your IP:\t{our_ip} ({get_our_country()})\nServer loc:\t{server_city} ({colo}) - ({server_country})'

    return preamble_str

# The rest of the code remains unchanged
# ...
```

---

### Summary of Changes:
- Replaced `requests.Session()` with `FuturesSession()` from `requests_futures`.
- Used `.result()` to block and retrieve the response from the `Future` object returned by `requests_futures`.
- No other changes were made to the logic or structure of the code.