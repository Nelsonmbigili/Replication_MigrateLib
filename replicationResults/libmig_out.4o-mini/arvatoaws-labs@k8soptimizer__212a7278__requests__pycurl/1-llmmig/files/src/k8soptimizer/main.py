import argparse
import json
import logging
import os
import re
import sys
import time
import pycurl
from io import BytesIO

from beartype import beartype
from beartype.typing import Optional, Tuple
from kubernetes import client, config
from kubernetes.client.models import (
    V1Container,
    V1Deployment,
    V1DeploymentList,
    V1NamespaceList,
    V2HorizontalPodAutoscaler,
)
from pythonjsonlogger import jsonlogger

from . import __version__, helpers

__author__ = "Philipp Hellmich"
__copyright__ = "Arvato Systems GmbH"
__license__ = "MIT"

__domain__ = "arvato-aws.io"

_logger = logging.getLogger(__name__)

PROMETHEUS_URL = os.getenv("PROMETHEUS_URL", "http://localhost:9090")

# ... (rest of the code remains unchanged)

@beartype
def query_prometheus(query: str) -> dict:
    """
    Query Prometheus API with the specified query string.

    Args:
        query (str): The Prometheus query string.

    Returns:
        dict: The JSON response from the Prometheus API.

    Raises:
        RuntimeError: If the response is missing expected data fields.

    Example:
        response = query_prometheus('sum(rate(http_requests_total{job="api"}[5m]))')
    """
    _logger.debug("Query to prometheus: %s", query)
    
    # Prepare the URL
    url = PROMETHEUS_URL + "/api/v1/query"
    
    # Prepare the response buffer
    response_buffer = BytesIO()
    
    # Initialize pycurl
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, response_buffer)
    curl.setopt(curl.POSTFIELDS, f"query={query}")
    
    try:
        curl.perform()
        http_code = curl.getinfo(curl.RESPONSE_CODE)
        if http_code != 200:
            raise RuntimeError(f"HTTP request failed with status code: {http_code}")
    finally:
        curl.close()
    
    # Get the response data
    response_data = response_buffer.getvalue().decode('utf-8')
    j = json.loads(response_data)
    _logger.debug("Response from prometheus: %s", j)
    
    if "data" not in j:
        raise RuntimeError("Got invalid results from query: {}".format(query))
    if "result" not in j["data"]:
        raise RuntimeError("Got invalid results from query: {}".format(query))
    return j

@beartype
def verify_prometheus_connection() -> bool:
    """
    Verify connection to the Prometheus API.

    Returns:
        bool: True if the connection is successful, False otherwise.

    Raises:
        RuntimeError: If the response is missing expected data fields or the connection fails.

    Example:
        connection_successful = verify_prometheus_connection()
    """
    url = PROMETHEUS_URL + "/api/v1/status/buildinfo"
    response_buffer = BytesIO()
    
    curl = pycurl.Curl()
    curl.setopt(curl.URL, url)
    curl.setopt(curl.WRITEDATA, response_buffer)
    
    try:
        curl.perform()
        http_code = curl.getinfo(curl.RESPONSE_CODE)
        if http_code != 200:
            raise RuntimeError(f"HTTP request failed with status code: {http_code}")
    finally:
        curl.close()
    
    response_data = response_buffer.getvalue().decode('utf-8')
    j = json.loads(response_data)
    _logger.debug(j)
    
    if "status" not in j:
        raise RuntimeError("Got invalid results request: {}".format(response_data))
    if j["status"] == "success":
        return True
    raise RuntimeError("Connection to prometheus api failed")

# ... (rest of the code remains unchanged)
