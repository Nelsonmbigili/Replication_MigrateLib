### Explanation of Changes:
To migrate the code from using `urllib3` to `requests`, the following changes were made:
1. **Replaced `urllib3.PoolManager` with `requests`**:
   - Removed the import of `urllib3.PoolManager`.
   - Replaced the `PoolManager` instance (`self.http`) with `requests` for making HTTP requests.
2. **Updated `_get` Method**:
   - Replaced the `urllib3`-based `self.http.request("GET", url)` with `requests.get(url)`.
   - Adjusted the response handling to use `requests`' response object (`response.status_code`, `response.text`, etc.).
3. **Removed `self.http` Initialization**:
   - Since `requests` does not require a persistent connection pool like `urllib3.PoolManager`, the initialization of `self.http` was removed.

### Modified Code:
Below is the updated code with the migration to `requests`:

```python
import requests  # Added import for requests

class FeatureRepository(object):
    def __init__(self) -> None:
        self.cache: AbstractFeatureCache = InMemoryFeatureCache()
        self.sse_client: Optional[SSEClient] = None

    def set_cache(self, cache: AbstractFeatureCache) -> None:
        self.cache = cache

    def clear_cache(self):
        self.cache.clear()

    def save_in_cache(self, key: str, res, ttl: int = 60):
        self.cache.set(key, res, ttl)

    # Loads features with an in-memory cache in front
    def load_features(
        self, api_host: str, client_key: str, decryption_key: str = "", ttl: int = 60
    ) -> Optional[Dict]:
        key = api_host + "::" + client_key

        cached = self.cache.get(key)
        if not cached:
            res = self._fetch_features(api_host, client_key, decryption_key)
            if res is not None:
                self.cache.set(key, res, ttl)
                logger.debug("Fetched features from API, stored in cache")
                return res
        return cached
    
    async def load_features_async(
        self, api_host: str, client_key: str, decryption_key: str = "", ttl: int = 60
    ) -> Optional[Dict]:
        key = api_host + "::" + client_key

        cached = self.cache.get(key)
        if not cached:
            res = await self._fetch_features_async(api_host, client_key, decryption_key)
            if res is not None:
                self.cache.set(key, res, ttl)
                logger.debug("Fetched features from API, stored in cache")
                return res
        return cached

    # Perform the GET request (separate method for easy mocking)
    def _get(self, url: str):
        response = requests.get(url)  # Replaced urllib3 with requests
        return response
    
    def _fetch_and_decode(self, api_host: str, client_key: str) -> Optional[Dict]:
        try:
            r = self._get(self._get_features_url(api_host, client_key))
            if r.status_code >= 400:  # Updated to use requests' status_code
                logger.warning(
                    "Failed to fetch features, received status code %d", r.status_code
                )
                return None
            decoded = json.loads(r.text)  # Updated to use requests' text attribute
            return decoded
        except Exception:
            logger.warning("Failed to decode feature JSON from GrowthBook API")
            return None
        
    async def _fetch_and_decode_async(self, api_host: str, client_key: str) -> Optional[Dict]:
        try:
            url = self._get_features_url(api_host, client_key)
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status >= 400:
                        logger.warning("Failed to fetch features, received status code %d", response.status)
                        return None
                    decoded = await response.json()
                    return decoded
        except aiohttp.ClientError as e:
            logger.warning(f"HTTP request failed: {e}")
            return None
        except Exception as e:
            logger.warning("Failed to decode feature JSON from GrowthBook API: %s", e)
            return None
        
    def decrypt_response(self, data, decryption_key: str):
        if "encryptedFeatures" in data:
            if not decryption_key:
                raise ValueError("Must specify decryption_key")
            try:
                decryptedFeatures = decrypt(data["encryptedFeatures"], decryption_key)
                data['features'] = json.loads(decryptedFeatures)
                del data['encryptedFeatures']
            except Exception:
                logger.warning(
                    "Failed to decrypt features from GrowthBook API response"
                )
                return None
        elif "features" not in data:
            logger.warning("GrowthBook API response missing features")
        
        if "encryptedSavedGroups" in data:
            if not decryption_key:
                raise ValueError("Must specify decryption_key")
            try:
                decryptedFeatures = decrypt(data["encryptedSavedGroups"], decryption_key)
                data['savedGroups'] = json.loads(decryptedFeatures)
                del data['encryptedSavedGroups']
                return data
            except Exception:
                logger.warning(
                    "Failed to decrypt saved groups from GrowthBook API response"
                )
            
        return data

    # Fetch features from the GrowthBook API
    def _fetch_features(
        self, api_host: str, client_key: str, decryption_key: str = ""
    ) -> Optional[Dict]:
        decoded = self._fetch_and_decode(api_host, client_key)
        if not decoded:
            return None

        data = self.decrypt_response(decoded, decryption_key)

        return data
        
    async def _fetch_features_async(
        self, api_host: str, client_key: str, decryption_key: str = ""
    ) -> Optional[Dict]:
        decoded = await self._fetch_and_decode_async(api_host, client_key)
        if not decoded:
            return None

        data = self.decrypt_response(decoded, decryption_key)

        return data


    def startAutoRefresh(self, api_host, client_key, cb):
        self.sse_client = self.sse_client or SSEClient(api_host=api_host, client_key=client_key, on_event=cb)
        self.sse_client.connect()

    def stopAutoRefresh(self):
        self.sse_client.disconnect()

    @staticmethod
    def _get_features_url(api_host: str, client_key: str) -> str:
        api_host = (api_host or "https://cdn.growthbook.io").rstrip("/")
        return api_host + "/api/features/" + client_key


# Singleton instance
feature_repo = FeatureRepository()
```

### Key Points:
- The `requests` library is now used for all HTTP requests.
- The `urllib3.PoolManager` and its initialization were removed.
- The `_get` method and response handling were updated to align with `requests`' API.