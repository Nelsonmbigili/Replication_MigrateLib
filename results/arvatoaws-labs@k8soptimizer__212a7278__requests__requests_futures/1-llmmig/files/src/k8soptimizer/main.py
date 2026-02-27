from requests_futures.sessions import FuturesSession

# Initialize a FuturesSession for asynchronous requests
session = FuturesSession()

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
    future_response = session.get(PROMETHEUS_URL + "/api/v1/query", params={"query": query})
    response = future_response.result()  # Block and get the actual response
    j = json.loads(response.text)
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
    future_response = session.get(PROMETHEUS_URL + "/api/v1/status/buildinfo")
    response = future_response.result()  # Block and get the actual response
    j = json.loads(response.text)
    _logger.debug(j)
    if "status" not in j:
        raise RuntimeError("Got invalid results request: {}".format(response.text))
    if j["status"] == "success":
        return True
    raise RuntimeError("Connection to prometheus api failed")
