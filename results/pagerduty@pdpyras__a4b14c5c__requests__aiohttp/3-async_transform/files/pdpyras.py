import aiohttp
import asyncio
import logging
from copy import deepcopy
from typing import Union, Iterator

TIMEOUT = 60
TEXT_LEN_LIMIT = 100

class PDSession:
    """
    Base class for making HTTP requests to PagerDuty APIs using aiohttp.
    """

    def __init__(self, api_key: str, debug=False):
        self.api_key = api_key
        self.headers = {
            "Authorization": f"Token token={api_key}",
            "Accept": "application/vnd.pagerduty+json;version=2",
        }
        self.timeout = aiohttp.ClientTimeout(total=TIMEOUT)
        self.log = logging.getLogger(__name__)
        self.debug = debug

    async def request(self, method: str, url: str, **kwargs) -> aiohttp.ClientResponse:
        """
        Make a generic PagerDuty API request using aiohttp.

        :param method: HTTP method (GET, POST, PUT, DELETE).
        :param url: The full URL to request.
        :param kwargs: Additional arguments for the request.
        :return: aiohttp.ClientResponse object.
        """
        async with aiohttp.ClientSession(timeout=self.timeout) as session:
            try:
                async with session.request(method, url, headers=self.headers, **kwargs) as response:
                    await self._handle_response(response)
                    return response
            except aiohttp.ClientError as e:
                self.log.error(f"HTTP request failed: {e}")
                raise

    async def _handle_response(self, response: aiohttp.ClientResponse):
        """
        Handle the HTTP response, raising exceptions for errors.

        :param response: aiohttp.ClientResponse object.
        """
        if response.status >= 400:
            error_text = await response.text()
            self.log.error(f"HTTP error {response.status}: {error_text}")
            response.raise_for_status()

    async def get(self, url: str, **kwargs) -> Union[dict, list]:
        """
        Perform a GET request and return the JSON-decoded response.

        :param url: The full URL to request.
        :param kwargs: Additional arguments for the request.
        :return: JSON-decoded response.
        """
        response = await self.request("GET", url, **kwargs)
        return await response.json()

    async def post(self, url: str, **kwargs) -> Union[dict, list]:
        """
        Perform a POST request and return the JSON-decoded response.

        :param url: The full URL to request.
        :param kwargs: Additional arguments for the request.
        :return: JSON-decoded response.
        """
        response = await self.request("POST", url, **kwargs)
        return await response.json()

    async def put(self, url: str, **kwargs) -> Union[dict, list]:
        """
        Perform a PUT request and return the JSON-decoded response.

        :param url: The full URL to request.
        :param kwargs: Additional arguments for the request.
        :return: JSON-decoded response.
        """
        response = await self.request("PUT", url, **kwargs)
        return await response.json()

    async def delete(self, url: str, **kwargs) -> None:
        """
        Perform a DELETE request.

        :param url: The full URL to request.
        :param kwargs: Additional arguments for the request.
        """
        await self.request("DELETE", url, **kwargs)

    async def iter_all(self, url: str, params=None, page_size=100) -> Iterator[dict]:
        """
        Iterate over all results from a paginated endpoint.

        :param url: The full URL to request.
        :param params: Query parameters for the request.
        :param page_size: Number of results per page.
        :return: Iterator over results.
        """
        params = params or {}
        params["limit"] = page_size
        offset = 0

        while True:
            params["offset"] = offset
            response = await self.get(url, params=params)
            results = response.get("data", [])
            for result in results:
                yield result

            if not response.get("more", False):
                break
            offset += page_size

# Example usage
async def main():
    api_key = "your_api_key"
    session = PDSession(api_key)

    # Example GET request
    users = await session.get("https://api.pagerduty.com/users")
    print(users)

    # Example POST request
    new_user = await session.post("https://api.pagerduty.com/users", json={"name": "New User"})
    print(new_user)

# Run the example
if __name__ == "__main__":
    asyncio.run(main())
