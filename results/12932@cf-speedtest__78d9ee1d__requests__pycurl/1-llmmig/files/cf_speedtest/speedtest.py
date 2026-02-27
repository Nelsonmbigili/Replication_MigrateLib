#! /usr/bin/env python3
from __future__ import annotations

import argparse
import math
import statistics
import time
from timeit import default_timer as timer
import io
import pycurl

import cf_speedtest.locations as locations
import cf_speedtest.options as options

CGI_ENDPOINT = 'https://speed.cloudflare.com/cdn-cgi/trace'
DOWNLOAD_ENDPOINT = 'https://speed.cloudflare.com/__down?measId=0&bytes={}'
UPLOAD_ENDPOINT = 'https://speed.cloudflare.com/__up?measId=0'

UPLOAD_HEADERS = [
    'Connection: keep-alive',
    'DNT: 1',
    'Content-Type: text/plain;charset=UTF-8',
    'Accept: */*',
]

PROXY_DICT = None
VERIFY_SSL = True
OUTPUT_FILE = None


def make_request(url, method='GET', headers=None, data=None):
    """Helper function to make HTTP requests using pycurl."""
    buffer = io.BytesIO()
    header_buffer = io.BytesIO()
    curl = pycurl.Curl()

    try:
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEDATA, buffer)
        curl.setopt(pycurl.HEADERFUNCTION, header_buffer)

        if headers:
            curl.setopt(pycurl.HTTPHEADER, headers)

        if method == 'POST':
            curl.setopt(pycurl.POST, 1)
            if data:
                curl.setopt(pycurl.POSTFIELDS, data)

        if not VERIFY_SSL:
            curl.setopt(pycurl.SSL_VERIFYPEER, 0)
            curl.setopt(pycurl.SSL_VERIFYHOST, 0)

        if PROXY_DICT:
            proxy = PROXY_DICT.get('http') or PROXY_DICT.get('https')
            if proxy:
                curl.setopt(pycurl.PROXY, proxy)

        curl.perform()

        response_code = curl.getinfo(pycurl.RESPONSE_CODE)
        response_body = buffer.getvalue().decode('utf-8')
        response_headers = header_buffer.getvalue().decode('utf-8')

        return response_code, response_body, response_headers

    except pycurl.error as e:
        raise RuntimeError(f"pycurl error: {e}")

    finally:
        curl.close()


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


def upload_test(total_bytes: int) -> int | float:
    start = timer()

    data = bytearray(total_bytes)
    response_code, response_body, response_headers = make_request(
        UPLOAD_ENDPOINT, method='POST', headers=UPLOAD_HEADERS, data=data
    )

    if response_code != 200:
        raise RuntimeError(f"Upload failed with status code {response_code}")

    total_time_taken = timer() - start

    server_time_taken = get_server_timing(response_headers)

    if OUTPUT_FILE:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as datafile:
            datafile.write(
                f'{time.time()},up,{total_bytes},{total_time_taken},{server_time_taken}\n',
            )

    return total_bytes, server_time_taken


def download_test(total_bytes: int) -> int | float:
    endpoint = DOWNLOAD_ENDPOINT.format(total_bytes)
    start = timer()

    response_code, response_body, response_headers = make_request(endpoint)

    if response_code != 200:
        raise RuntimeError(f"Download failed with status code {response_code}")

    total_time_taken = timer() - start

    content_size = len(response_body)
    server_time_taken = get_server_timing(response_headers)

    if OUTPUT_FILE:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as datafile:
            datafile.write(
                f'{time.time()},down,{content_size},{total_time_taken},{server_time_taken}\n',
            )

    return content_size, total_time_taken - server_time_taken


def latency_test() -> float:
    endpoint = DOWNLOAD_ENDPOINT.format(0)

    start = timer()
    response_code, response_body, response_headers = make_request(endpoint)

    if response_code != 200:
        raise RuntimeError(f"Latency test failed with status code {response_code}")

    total_time_taken = timer() - start
    server_time_taken = get_server_timing(response_headers)

    if OUTPUT_FILE:
        with open(OUTPUT_FILE, 'a', encoding='utf-8') as datafile:
            datafile.write(
                f'{time.time()},down,{len(response_body)},{total_time_taken},{server_time_taken}\n',
            )

    return total_time_taken - server_time_taken


def get_our_country() -> str:
    response_code, response_body, _ = make_request(CGI_ENDPOINT)

    if response_code != 200:
        raise RuntimeError(f"Failed to get country with status code {response_code}")

    cgi_data = response_body
    cgi_dict = {
        k: v for k, v in [
            line.split(
                '=',
            ) for line in cgi_data.splitlines()
        ]
    }

    return cgi_dict.get('loc') or 'Unknown'


def preamble() -> str:
    response_code, response_body, response_headers = make_request(
        DOWNLOAD_ENDPOINT.format(0)
    )

    if response_code != 200:
        raise RuntimeError(f"Preamble request failed with status code {response_code}")

    our_ip = response_headers.get('cf-meta-ip')
    colo = response_headers.get('cf-meta-colo')
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
