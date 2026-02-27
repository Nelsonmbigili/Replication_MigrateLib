### Explanation of Changes

To migrate the code from `fastapi` to `sanic`, the following changes were made:

1. **Sanic Application Setup**:
   - Replaced `FastAPI` with `Sanic` for creating the application instance.
   - Used `Sanic`'s `before_server_start` and `after_server_stop` hooks to replace `on_startup` and `on_shutdown` lifecycle events.

2. **Route Definitions**:
   - Replaced `@app.get` and `@app.post` decorators with `@app.route` in `Sanic`. The HTTP methods are specified using the `methods` parameter.

3. **Request and Response Handling**:
   - Replaced `fastapi.requests.Request` with `sanic.request.Request`.
   - Replaced `fastapi.responses.Response` with `sanic.response.raw` for raw responses and `sanic.response.json` for JSON responses.

4. **Logging**:
   - Replaced `fastapi.logger` with Python's standard `logging` module, as `Sanic` does not provide a built-in logger like `FastAPI`.

5. **Development Server**:
   - Replaced `uvicorn.run` with `app.run` for running the `Sanic` application.

Below is the modified code:

---

### Modified Code

```python
import asyncio
import logging
from collections.abc import Coroutine
from socket import AF_INET
from typing import List, Optional, Any, Dict

import aiohttp
from sanic import Sanic
from sanic.request import Request
from sanic.response import raw, json

SIZE_POOL_AIOHTTP = 100

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("sanic_app")


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
            return {"ERROR": str(e)}

        return json_result


async def on_start_up(app: Sanic) -> None:
    logger.info("on_start_up")
    SingletonAiohttp.get_aiohttp_client()


async def on_shutdown(app: Sanic) -> None:
    logger.info("on_shutdown")
    await SingletonAiohttp.close_aiohttp_client()


app = Sanic("SanicApp")
app.register_listener(on_start_up, "before_server_start")
app.register_listener(on_shutdown, "after_server_stop")


@app.route('/endpoint', methods=["GET"])
async def endpoint(request: Request) -> Any:
    url = "http://localhost:8080/test"
    result = await SingletonAiohttp.query_url(url)
    return json(result)


@app.route('/endpoint_multi', methods=["GET"])
async def endpoint_multi(request: Request) -> Dict[str, int]:
    url = "http://localhost:8080/test"

    async_calls: List[Coroutine[Any, Any, Any]] = list()  # store all async operations

    async_calls.append(SingletonAiohttp.query_url(url))
    async_calls.append(SingletonAiohttp.query_url(url))

    all_results: List[Dict[Any, Any]] = await asyncio.gather(*async_calls)  # wait for all async operations
    return json({'success': sum([x['success'] for x in all_results])})


@app.route("/endpoint_stream/", methods=["POST"])
async def endpoint_stream(request: Request):
    body = b'RST'
    async for chunk in request.body:
        body += chunk

    return raw(body, content_type='text/plain')


if __name__ == '__main__':  # local dev
    app.run(host="0.0.0.0", port=8000)
```

---

### Key Notes:
- The `Sanic` framework uses `register_listener` to handle lifecycle events like `before_server_start` and `after_server_stop`.
- The `Sanic` request object (`sanic.request.Request`) provides a `body` attribute for streaming data, which replaces `request.stream()` in `FastAPI`.
- The `Sanic` response module (`sanic.response`) provides `raw` for raw responses and `json` for JSON responses.
- Logging is handled using Python's standard `logging` module instead of `fastapi.logger`.

This code maintains the original functionality while adhering to the `Sanic` framework's conventions.