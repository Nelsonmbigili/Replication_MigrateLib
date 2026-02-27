import pycurl
from io import BytesIO

# ... (other imports remain unchanged)

# Replacing the `requests.get` calls in the `query_prometheus` function
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
    
    # Prepare the URL and query parameters
    url = f"{PROMETHEUS_URL}/api/v1/query?query={query}"
    buffer = BytesIO()
    
    # Initialize pycurl
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    
    try:
        # Perform the request
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        curl.close()
        
        # Check for HTTP errors
        if status_code != 200:
            raise RuntimeError(f"HTTP error {status_code} for query: {query}")
        
        # Parse the response
        response_text = buffer.getvalue().decode('utf-8')
        j = json.loads(response_text)
        _logger.debug("Response from prometheus: %s", j)
        
        # Validate the response structure
        if "data" not in j:
            raise RuntimeError("Got invalid results from query: {}".format(query))
        if "result" not in j["data"]:
            raise RuntimeError("Got invalid results from query: {}".format(query))
        
        return j
    except pycurl.error as e:
        raise RuntimeError(f"Connection error: {e}")
    finally:
        buffer.close()


# Replacing the `requests.get` calls in the `verify_prometheus_connection` function
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
    url = f"{PROMETHEUS_URL}/api/v1/status/buildinfo"
    buffer = BytesIO()
    
    # Initialize pycurl
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, url)
    curl.setopt(pycurl.WRITEFUNCTION, buffer.write)
    
    try:
        # Perform the request
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        curl.close()
        
        # Check for HTTP errors
        if status_code != 200:
            raise RuntimeError(f"HTTP error {status_code} while verifying Prometheus connection")
        
        # Parse the response
        response_text = buffer.getvalue().decode('utf-8')
        j = json.loads(response_text)
        _logger.debug(j)
        
        # Validate the response structure
        if "status" not in j:
            raise RuntimeError("Got invalid results request: {}".format(response_text))
        if j["status"] == "success":
            return True
        
        raise RuntimeError("Connection to prometheus api failed")
    except pycurl.error as e:
        raise RuntimeError(f"Connection error: {e}")
    finally:
        buffer.close()
