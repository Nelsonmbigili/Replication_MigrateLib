import argparse
import json
import logging
import os
import re
import sys
import time

import urllib3
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

# Create a PoolManager instance for managing HTTP connections
http = urllib3.PoolManager()

@beartype
def query_prometheus(query: str) -> dict:
    """
    Query Prometheus API with the specified query string.

    Args:
        query (str): The Prometheus query string.

    Returns:
        dict: The JSON response from the Prometheus API.

    Raises:
        RuntimeError: If the response is missing expected data fields or if the HTTP request fails.
    """
    _logger.debug("Query to prometheus: %s", query)
    url = f"{PROMETHEUS_URL}/api/v1/query"
    response = http.request("GET", url, fields={"query": query})

    if response.status != 200:
        raise RuntimeError(f"Failed to query Prometheus: HTTP {response.status}")

    j = json.loads(response.data.decode("utf-8"))
    _logger.debug("Response from prometheus: %s", j)

    if "data" not in j or "result" not in j["data"]:
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
    """
    url = f"{PROMETHEUS_URL}/api/v1/status/buildinfo"
    response = http.request("GET", url)

    if response.status != 200:
        raise RuntimeError(f"Failed to connect to Prometheus: HTTP {response.status}")

    j = json.loads(response.data.decode("utf-8"))
    _logger.debug(j)

    if "status" not in j:
        raise RuntimeError("Got invalid results request: {}".format(response.data.decode("utf-8")))

    if j["status"] == "success":
        return True

    raise RuntimeError("Connection to Prometheus API failed")
