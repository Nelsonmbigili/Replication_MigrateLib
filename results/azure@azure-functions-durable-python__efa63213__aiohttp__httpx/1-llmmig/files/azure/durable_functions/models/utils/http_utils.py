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
