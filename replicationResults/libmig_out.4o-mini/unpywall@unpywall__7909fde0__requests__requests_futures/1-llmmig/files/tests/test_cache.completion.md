### Explanation of Changes
To migrate the code from using the `requests` library to the `requests_futures` library, the following changes were made:

1. **Import Statement**: The import statement for `Response` from `requests` remains unchanged, as `requests_futures` still uses the same `Response` class.
2. **Using Futures**: The `requests_futures` library allows for asynchronous requests. Therefore, the `get` method calls need to be modified to use the `FuturesSession` class from `requests_futures`. This involves creating a `FuturesSession` instance and using it to make the requests.
3. **Handling Responses**: Since the requests are now asynchronous, the response handling needs to be adjusted to wait for the future to complete before accessing the response.

Here is the modified code:

```python
import pytest
import os
import time
import uuid
from requests import Response
from requests_futures.sessions import FuturesSession
from shutil import copyfile

from unpywall.cache import UnpywallCache

os.environ['UNPAYWALL_EMAIL'] = 'bganglia892@gmail.com'


class TestUnpywallCache:

    test_dir = os.path.abspath(os.path.dirname(__file__))
    test_backup_cache_path = os.path.join(test_dir, 'unpaywall_cache')
    test_cache_path = os.path.join(test_dir, 'test_cache')

    @pytest.fixture
    def backup_cache(self):
        cache = UnpywallCache(TestUnpywallCache.test_backup_cache_path)
        yield cache

    @pytest.fixture
    def example_cache(self):

        if os.path.exists(TestUnpywallCache.test_cache_path):
            os.remove(TestUnpywallCache.test_cache_path)
            assert UnpywallCache(
                    TestUnpywallCache.test_cache_path).content == {}
            assert UnpywallCache(
                    TestUnpywallCache.test_cache_path).access_times == {}

        copyfile(TestUnpywallCache.test_backup_cache_path,
                 TestUnpywallCache.test_cache_path)
        cache = UnpywallCache(TestUnpywallCache.test_cache_path)
        assert cache.content != {}
        assert cache.access_times != {}
        yield cache

    def test_reset_cache(self, example_cache):
        example_cache.reset_cache()
        assert example_cache.content == {}
        assert example_cache.access_times == {}

    def test_delete(self, example_cache):
        doi = '10.1016/j.tmaid.2020.101663'
        assert doi in example_cache.content
        assert doi in example_cache.access_times
        example_cache.delete(doi)
        assert doi not in example_cache.content
        assert doi not in example_cache.access_times

    def test_timeout(self, example_cache):
        timeout = 1
        doi = '10.1016/j.jns.2020.116832'
        example_cache.timeout = timeout
        example_cache.delete(doi)
        assert doi not in example_cache.content
        future = example_cache.get(doi)
        time.sleep(timeout)
        assert example_cache.timed_out(doi)

    def test_get(self, example_cache, backup_cache):
        doi = '10.1016/j.jns.2020.116832'
        example_cache.delete(doi)
        assert doi not in example_cache.content
        assert doi not in example_cache.access_times
        session = FuturesSession()
        future_backup = session.get(backup_cache.get(doi))
        assert isinstance(future_backup.result(), Response)
        future_example = session.get(example_cache.get(doi, ignore_cache=True))
        assert isinstance(future_example.result(), Response)

    def test_save_load(self, example_cache, backup_cache):
        doi = '10.1016/j.jns.2020.116832'
        example_cache.delete(doi)
        assert doi not in example_cache.content
        assert doi not in example_cache.access_times
        session = FuturesSession()
        future_backup = session.get(backup_cache.get(doi))
        future_backup.result()  # Wait for the response
        saved_cache_name = str(uuid.uuid4().hex)
        example_cache.save(saved_cache_name)
        UnpywallCache(saved_cache_name)
        os.remove(saved_cache_name)
        path = os.path.join(os.getcwd(), 'unpaywall_cache')
        assert UnpywallCache().name == path
        os.remove(path)
        assert doi in backup_cache.content
        assert doi in backup_cache.access_times

    def test_download(self, example_cache):
        doi = '10.1016/j.jns.2020.116832'
        session = FuturesSession()
        future_download = session.get(example_cache.download(doi, 'raise'))
        assert isinstance(future_download.result(), Response)
```

### Summary of Changes
- Introduced `FuturesSession` from `requests_futures` to handle asynchronous requests.
- Adjusted the `get` method calls to use the `FuturesSession` and wait for the result using `.result()`.