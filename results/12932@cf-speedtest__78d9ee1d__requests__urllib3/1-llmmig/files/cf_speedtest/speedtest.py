#! /usr/bin/env python3
from __future__ import annotations

import argparse
import math
import statistics
import time
from timeit import default_timer as timer

import urllib3

import cf_speedtest.locations as locations
import cf_speedtest.options as options

# Initialize urllib3 PoolManager
HTTP_MANAGER = urllib3.PoolManager()

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

    response = HTTP_MANAGER.request(
        'POST',
        UPLOAD_ENDPOINT,
        body=bytearray(total_bytes),
        headers=UPLOAD_HEADERS,
        retries=False,
        cert_reqs='CERT_REQUIRED' if VERIFY_SSL else 'CERT_NONE',
    )

    if response.status != 200:
        raise Exception(f"HTTP Error: {response.status}")

    total_time_taken = timer() - start

    # trust what the server says as time taken
    server_time_taken = get_server_timing(response.headers.get('Server-Timing', ''))

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

    response = HTTP_MANAGER.request(
        'GET',
        endpoint,
        retries=False,
        cert_reqs='CERT_REQUIRED' if VERIFY_SSL else 'CERT_NONE',
    )

    if response.status != 200:
        raise Exception(f"HTTP Error: {response.status}")

    total_time_taken = timer() - start

    content_size = len(response.data)
    server_time_taken = get_server_timing(response.headers.get('Server-Timing', ''))

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
    response = HTTP_MANAGER.request(
        'GET',
        endpoint,
        retries=False,
        cert_reqs='CERT_REQUIRED' if VERIFY_SSL else 'CERT_NONE',
    )

    if response.status != 200:
        raise Exception(f"HTTP Error: {response.status}")

    total_time_taken = timer() - start
    server_time_taken = get_server_timing(response.headers.get('Server-Timing', ''))

    if OUTPUT_FILE:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as datafile:
            datafile.write(
                f'{time.time()},down,{len(response.data)},{total_time_taken},{server_time_taken}\n',
            )

    return total_time_taken - server_time_taken

# See https://speed.cloudflare.com/cdn-cgi/trace


def get_our_country() -> str:
    response = HTTP_MANAGER.request(
        'GET',
        CGI_ENDPOINT,
        retries=False,
        cert_reqs='CERT_REQUIRED' if VERIFY_SSL else 'CERT_NONE',
    )

    if response.status != 200:
        raise Exception(f"HTTP Error: {response.status}")

    cgi_data = response.data.decode()
    cgi_dict = {
        k: v for k, v in [
            line.split(
                '=',
            ) for line in cgi_data.splitlines()
        ]
    }

    return cgi_dict.get('loc') or 'Unknown'


def preamble() -> str:
    response = HTTP_MANAGER.request(
        'GET',
        DOWNLOAD_ENDPOINT.format(0),
        retries=False,
        cert_reqs='CERT_REQUIRED' if VERIFY_SSL else 'CERT_NONE',
    )

    if response.status != 200:
        raise Exception(f"HTTP Error: {response.status}")

    our_ip = response.headers.get('cf-meta-ip')
    colo = response.headers.get('cf-meta-colo')
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
