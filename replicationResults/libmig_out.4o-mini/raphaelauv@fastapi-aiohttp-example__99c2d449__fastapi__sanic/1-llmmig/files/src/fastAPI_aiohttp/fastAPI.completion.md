### Explanation of Changes

To migrate the code from using the `fastapi` library to the `sanic` library, the following changes were made:

1. **Import Statements**: Changed the import of `FastAPI`, `Request`, and `Response` from `fastapi` to their equivalents in `sanic`.
2. **Application Initialization**: Replaced `FastAPI` with `Sanic` for app initialization.
3. **Logging**: Removed the `fastAPI_logger` and used `app.logger` for logging in Sanic.
4. **Request Handling**: Adjusted the way to handle requests and responses to align with Sanic's API.
5. **Startup and Shutdown Events**: Changed the way startup and shutdown events are registered in Sanic.
6. **Running the Application**: Replaced `uvicorn.run` with `app.run` for running the Sanic application.

Here is the modified code:

```python
import asyncio
from collections.abc import Coroutine
from socket import AF_INET
from typing import List, Optional, Any, Dict

import aiohttp
from sanic import Sanic, response
from sanic.request import Request

SIZE_POOL_AIOHTTP = 100


class SingletonAiohttp:
    aiohttp_client: Optional[aiohttp.ClientSession] = None

    @classmethod
    def get_aiohttp_client(cls) -> aiohttp.ClientSession:
        if cls.aiohttp_client is None:
            timeout = aiohttp.ClientTimeout(total=2)
            connector = aiohttp.TCPConnector(family=AF_INET, limit_per_host=SIZE_POOL_AIOHTTP)
            cls.aiohttp_client = aiohttp.ClientSession(timeout=timeout, connector=connector)

        return cls.aiohttp_client

    @classmethod
    async def close_aiohttp_client(cls) -> None:
        if cls.aiohttp_client:
            await cls.aiohttp_client.close()
            cls.aiohttp_client = None

    @classmethod
    async def query_url(cls, url: str) -> Any:
        client = cls.get_aiohttp_client()

        try:
            async with client.post(url) as response:
                if response.status != 200:
                    return {"ERROR OCCURED" + str(await response.text())}

                json_result = await response.json()
        except Exception as e:
            return {"ERROR": e}

        return json_result


app = Sanic(__name__)


@app.listener('before_server_start')
async def on_start_up(app, loop):
    app.logger.info("on_start_up")
    SingletonAiohttp.get_aiohttp_client()


@app.listener('after_server_stop')
async def on_shutdown(app, loop):
    app.logger.info("on_shutdown")
    await SingletonAiohttp.close_aiohttp_client()


@app.get('/endpoint')
async def endpoint(request: Request) -> Any:
    url = "http://localhost:8080/test"
    return await SingletonAiohttp.query_url(url)


@app.get('/endpoint_multi')
async def endpoint_multi(request: Request) -> Dict[str, int]:
    url = "http://localhost:8080/test"

    async_calls: List[Coroutine[Any, Any, Any]] = list()  # store all async operations

    async_calls.append(SingletonAiohttp.query_url(url))
    async_calls.append(SingletonAiohttp.query_url(url))

    all_results: List[Dict[Any, Any]] = await asyncio.gather(*async_calls)  # wait for all async operations
    return {'success': sum([x['success'] for x in all_results])}


@app.post("/endpoint_stream/")
async def endpoint_stream(request: Request):
    body = b'RST'
    async for chunk in request.stream():
        body += chunk

    return response.text(body, content_type='text/plain')


if __name__ == '__main__':  # local dev
    app.run(host="0.0.0.0", port=8000)
``` 

This code now uses the `sanic` framework while maintaining the original structure and functionality of the application.