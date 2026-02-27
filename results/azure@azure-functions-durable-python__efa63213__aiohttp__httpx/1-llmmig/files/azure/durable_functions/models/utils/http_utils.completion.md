### Explanation of Changes
To migrate the code from `aiohttp` to `httpx`, the following changes were made:
1. **Library Import**: Replaced `aiohttp` with `httpx`.
2. **Session Management**: In `httpx`, the `httpx.AsyncClient` is used instead of `aiohttp.ClientSession`.
3. **Request Methods**: The `post`, `get`, and `delete` methods of `httpx.AsyncClient` are used, which are similar to `aiohttp`.
4. **Response Handling**: In `httpx`, the `response.json()` method does not require a `content_type` argument, as it automatically handles JSON decoding.
5. **Error Handling**: `httpx` raises exceptions for HTTP errors (e.g., 4xx or 5xx responses) by default. To mimic the behavior of `aiohttp`, where errors do not raise exceptions, the `response.raise_for_status()` method is not used.

### Modified Code
```python
from typing import Any, List, Union

import httpx


async def post_async_request(url: str, data: Any = None) -> List[Union[int, Any]]:
    """Post request with the data provided to the url provided.

    Parameters
    ----------
    url: str
        url to make the post to
    data: Any
        object to post

    Returns
    -------
    [int, Any]
        Tuple with the Response status code and the data returned from the request
    """
    async with httpx.AsyncClient() as client:
        response = await client.post(url, json=data)
        # httpx automatically handles JSON decoding
        data = response.json()
        return [response.status_code, data]


async def get_async_request(url: str) -> List[Any]:
    """Get the data from the url provided.

    Parameters
    ----------
    url: str
        url to get the data from

    Returns
    -------
    [int, Any]
        Tuple with the Response status code and the data returned from the request
    """
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
        if data is None:
            data = ""
        return [response.status_code, data]


async def delete_async_request(url: str) -> List[Union[int, Any]]:
    """Delete the data from the url provided.

    Parameters
    ----------
    url: str
        url to delete the data from

    Returns
    -------
    [int, Any]
        Tuple with the Response status code and the data returned from the request
    """
    async with httpx.AsyncClient() as client:
        response = await client.delete(url)
        data = response.json()
        return [response.status_code, data]
```

### Key Notes
- The migration is straightforward because both `aiohttp` and `httpx` provide similar asynchronous HTTP client functionality.
- The `httpx` library simplifies JSON decoding by not requiring a `content_type` argument.
- The behavior of not raising exceptions for HTTP errors is preserved by not calling `response.raise_for_status()`. If you want to enable exception raising for HTTP errors, you can explicitly call `response.raise_for_status()` after each request.