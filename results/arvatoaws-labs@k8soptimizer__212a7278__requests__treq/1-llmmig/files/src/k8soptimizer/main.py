import argparse
import json
import logging
import os
import re
import sys
import time
import asyncio

import treq
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

# Other constants remain unchanged...

@beartype
async def query_prometheus(query: str) -> dict:
    """
    Query Prometheus API with the specified query string.

    Args:
        query (str): The Prometheus query string.

    Returns:
        dict: The JSON response from the Prometheus API.

    Raises:
        RuntimeError: If the response is missing expected data fields.

    Example:
        response = await query_prometheus('sum(rate(http_requests_total{job="api"}[5m]))')
    """
    _logger.debug("Query to prometheus: %s", query)
    response = await treq.get(PROMETHEUS_URL + "/api/v1/query", params={"query": query})
    j = await response.json()
    _logger.debug("Response from prometheus: %s", j)
    if "data" not in j:
        raise RuntimeError("Got invalid results from query: {}".format(query))
    if "result" not in j["data"]:
        raise RuntimeError("Got invalid results from query: {}".format(query))
    return j


@beartype
async def verify_prometheus_connection() -> bool:
    """
    Verify connection to the Prometheus API.

    Returns:
        bool: True if the connection is successful, False otherwise.

    Raises:
        RuntimeError: If the response is missing expected data fields or the connection fails.

    Example:
        connection_successful = await verify_prometheus_connection()
    """
    response = await treq.get(PROMETHEUS_URL + "/api/v1/status/buildinfo")
    j = await response.json()
    _logger.debug(j)
    if "status" not in j:
        raise RuntimeError("Got invalid results request: {}".format(j))
    if j["status"] == "success":
        return True
    raise RuntimeError("Connection to prometheus api failed")


# Update all functions that call `query_prometheus` or `verify_prometheus_connection` to be asynchronous.
# For example:

@beartype
async def get_number_of_samples_from_history(
    namespace: str,
    workload: str,
    workload_type: str = "deployment",
    lookback_minutes: int = DEFAULT_LOOKBACK_MINUTES,
    offset_minutes: int = DEFAULT_OFFSET_MINUTES,
) -> int:
    """
    Get the CPU cores usage history for a specific container.

    Args:
        namespace (str): The name of the Kubernetes namespace.
        workload (str): The name of the workload (e.g., myapp).
        workload_type (str, optional): The type of workload. Default is "deployment".
        lookback_minutes (int, optional): The number of minutes to look back in time for the query. Default is DEFAULT_LOOKBACK_MINUTES.
        offset_minutes (int, optional): The offset in minutes for the query. Default is DEFAULT_OFFSET_MINUTES.

    Returns:
        float: The number of samples from prometheus.

    Raises:
        RuntimeError: If no data is found for the Prometheus query.

    Example:
        samples = await get_number_of_samples_from_history("my-namespace", "my-deployment")
    """
    query = 'max by (namespace,workload,workload_type) (count_over_time(kube_workload_container_resource_usage_cpu_cores_avg{{namespace="{namespace}", workload="{workload}", workload_type="{workload_type}"}}[{lookback_minutes}m] {offset_minutes_str}))'.format(
        namespace=namespace,
        workload=workload,
        workload_type=workload_type,
        lookback_minutes=lookback_minutes,
        offset_minutes_str=format_offset_minutes(offset_minutes),
    )
    j = await query_prometheus(query)

    if j["data"]["result"] == []:
        raise RuntimeError("No data found for prometheus query: {}".format(query))
    return int(j["data"]["result"][0]["value"][1])


# Update the `main` function to use asyncio:
async def main(args):
    args = parse_args(args)
    setup_logging(args.loglevel, args.logformat)
    extra = {}
    _logger.addFilter(AppFilter(extra))
    _logger.info("Starting k8soptimizer...")

    verify_kubernetes_connection()
    await verify_prometheus_connection()

    namespace_pattern = args.namespace_pattern
    if args.namespace is not None:
        namespace_pattern = "^{}$".format(args.namespace)
    deplopyment_pattern = args.deplopyment_pattern
    if args.deployment is not None:
        deplopyment_pattern = "^{}$".format(args.deployment)
    container_pattern = args.container_pattern
    if args.container is not None:
        container_pattern = "^{}$".format(args.container)

    lookback_minutes = args.lookback_minutes
    offset_minutes = args.offsett_minutes
    _logger.info("Using namespace_pattern: %s" % namespace_pattern)
    _logger.info("Using deplopyment_pattern: %s" % deplopyment_pattern)
    _logger.info("Using container_pattern: %s" % container_pattern)
    _logger.info("Using lookback_minutes: %s" % lookback_minutes)
    _logger.info("Using offset_minutes: %s" % offset_minutes)
    _logger.info("Using dry_run: %s" % args.dry_run)

    for namespace in get_namespaces(namespace_pattern).items:
        extra = {"namespace": namespace.metadata.name}
        _logger.addFilter(AppFilter(extra))
        for deployment in get_deployments(
            namespace.metadata.name, deplopyment_pattern
        ).items:
            try:
                await optimize_deployment(
                    deployment,
                    container_pattern,
                    lookback_minutes,
                    offset_minutes,
                    args.dry_run,
                )
                await asyncio.sleep(DELAY_BETWEEN_UPDATES)
            except Exception as e:
                _logger.warning(
                    "An error occurred while optimizing the deployment: %s" % str(e),
                    exc_info=True,
                )

    extra = {}
    _logger.addFilter(AppFilter(extra))

    print_stats()

    _logger.info("Finished k8soptimizer")


def run():
    asyncio.run(main(sys.argv[1:]))


if __name__ == "__main__":
    run()
