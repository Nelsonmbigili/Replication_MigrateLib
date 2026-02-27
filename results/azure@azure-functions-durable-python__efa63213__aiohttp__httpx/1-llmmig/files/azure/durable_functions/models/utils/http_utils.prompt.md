The following Python code currently uses the library "aiohttp" version 3.7.4.
Migrate this code to use the library "httpx" version 0.28.1 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "aiohttp" to "httpx".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "aiohttp" and "httpx".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from typing import Any, List, Union

import aiohttp


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
    async with aiohttp.ClientSession() as session:
        async with session.post(url,
                                json=data) as response:
            # We disable aiohttp's input type validation
            # as the server may respond with alternative
            # data encodings. This is potentially unsafe.
            # More here: https://docs.aiohttp.org/en/stable/client_advanced.html
            data = await response.json(content_type=None)
            return [response.status, data]


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
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json(content_type=None)
            if data is None:
                data = ""
            return [response.status, data]


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
    async with aiohttp.ClientSession() as session:
        async with session.delete(url) as response:
            data = await response.json(content_type=None)
            return [response.status, data]

```