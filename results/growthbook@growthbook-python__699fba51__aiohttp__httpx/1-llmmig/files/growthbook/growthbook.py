import httpx
from httpx import RequestError, HTTPStatusError

class SSEClient:
    def __init__(self, api_host, client_key, on_event, reconnect_delay=5, headers=None):
        self.api_host = api_host
        self.client_key = client_key

        self.on_event = on_event
        self.reconnect_delay = reconnect_delay

        self._sse_client = None
        self._sse_thread = None
        self._loop = None

        self.is_running = False

        self.headers = {
            "Accept": "application/json; q=0.5, text/event-stream",
            "Cache-Control": "no-cache",
        }

        if headers:
            self.headers.update(headers)

    def connect(self):
        if self.is_running:
            logger.debug("Streaming session is already running.")
            return

        self.is_running = True
        self._sse_thread = threading.Thread(target=self._run_sse_channel)
        self._sse_thread.start()

    def disconnect(self):
        self.is_running = False
        if self._loop and self._loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._stop_session(), self._loop)
            try:
                future.result()
            except Exception as e:
                logger.error(f"Streaming disconnect error: {e}")

        if self._sse_thread:
            self._sse_thread.join(timeout=5)

        logger.debug("Streaming session disconnected")

    def _get_sse_url(self, api_host: str, client_key: str) -> str:
        api_host = (api_host or "https://cdn.growthbook.io").rstrip("/")
        return f"{api_host}/sub/{client_key}"

    async def _init_session(self):
        url = self._get_sse_url(self.api_host, self.client_key)
        
        while self.is_running:
            try:
                async with httpx.AsyncClient(headers=self.headers) as client:
                    self._sse_client = client

                    async with client.stream("GET", url) as response:
                        response.raise_for_status()
                        await self._process_response(response)
            except HTTPStatusError as e:
                logger.error(f"Streaming error, closing connection: {e.response.status_code} {e.response.text}")
                self.is_running = False
                break
            except RequestError as e:
                logger.error(f"Streaming error: {e}")
                if not self.is_running:
                    break
                await self._wait_for_reconnect()
            except TimeoutError:
                logger.warning(f"Streaming connection timed out.")
                await self._wait_for_reconnect()
            except asyncio.CancelledError:
                logger.debug("Streaming was cancelled.")
                break
            finally:
                await self._close_session()

    async def _process_response(self, response):
        event_data = {}
        async for line in response.aiter_lines():
            decoded_line = line.strip()
            if decoded_line.startswith("event:"):
                event_data['type'] = decoded_line[len("event:"):].strip()
            elif decoded_line.startswith("data:"):
                event_data['data'] = event_data.get('data', '') + f"\n{decoded_line[len('data:'):].strip()}"
            elif not decoded_line:
                if 'type' in event_data and 'data' in event_data:
                    self.on_event(event_data)
                event_data = {}

        if 'type' in event_data and 'data' in event_data:
            self.on_event(event_data)

    async def _wait_for_reconnect(self):
        logger.debug(f"Attempting to reconnect streaming in {self.reconnect_delay}")
        await asyncio.sleep(self.reconnect_delay)

    async def _close_session(self):
        if self._sse_client:
            await self._sse_client.aclose()
            logger.debug("Streaming session closed.")

    def _run_sse_channel(self):
        self._loop = asyncio.new_event_loop()
        
        try:
            self._loop.run_until_complete(self._init_session())
        except asyncio.CancelledError:
            pass
        finally:
            self._loop.run_until_complete(self._loop.shutdown_asyncgens())
            self._loop.close()

    async def _stop_session(self):
        if self._sse_client:
            await self._sse_client.aclose()

        if self._loop and self._loop.is_running():
            tasks = [task for task in asyncio.all_tasks(self._loop) if not task.done()]
            for task in tasks:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass


class FeatureRepository(object):
    def __init__(self) -> None:
        self.cache: AbstractFeatureCache = InMemoryFeatureCache()
        self.http: Optional[PoolManager] = None
        self.sse_client: Optional[SSEClient] = None

    async def _fetch_and_decode_async(self, api_host: str, client_key: str) -> Optional[Dict]:
        try:
            url = self._get_features_url(api_host, client_key)
            async with httpx.AsyncClient() as client:
                response = await client.get(url)
                if response.status_code >= 400:
                    logger.warning("Failed to fetch features, received status code %d", response.status_code)
                    return None
                decoded = response.json()
                return decoded
        except RequestError as e:
            logger.warning(f"HTTP request failed: {e}")
            return None
        except Exception as e:
            logger.warning("Failed to decode feature JSON from GrowthBook API: %s", e)
            return None
