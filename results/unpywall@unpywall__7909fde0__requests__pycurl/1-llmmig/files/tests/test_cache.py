import pytest
import os
import time
import uuid
import pycurl
from io import BytesIO
from shutil import copyfile

from unpywall.cache import UnpywallCache

os.environ['UNPAYWALL_EMAIL'] = 'bganglia892@gmail.com'


class PycurlResponse:
    """Custom response class to simulate requests.Response using pycurl."""
    def __init__(self, status_code, headers, body):
        self.status_code = status_code
        self.headers = headers
        self.body = body

    def json(self):
        """Parse the body as JSON."""
        import json
        return json.loads(self.body)


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
        example_cache.get(doi)
        time.sleep(timeout)
        assert example_cache.timed_out(doi)

    def test_get(self, example_cache, backup_cache):
        doi = '10.1016/j.jns.2020.116832'
        example_cache.delete(doi)
        assert doi not in example_cache.content
        assert doi not in example_cache.access_times
        assert isinstance(backup_cache.get(doi), PycurlResponse)
        assert isinstance(example_cache.get(doi, ignore_cache=True), PycurlResponse)

    def test_save_load(self, example_cache, backup_cache):
        doi = '10.1016/j.jns.2020.116832'
        example_cache.delete(doi)
        assert doi not in example_cache.content
        assert doi not in example_cache.access_times
        backup_cache.get(doi)
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
        assert isinstance(example_cache.download(doi, 'raise'), PycurlResponse)


# Update UnpywallCache methods to use pycurl
class UnpywallCache:
    # Other methods remain unchanged

    def get(self, doi, ignore_cache=False):
        """Fetch data using pycurl."""
        buffer = BytesIO()
        headers = {}

        curl = pycurl.Curl()
        curl.setopt(curl.URL, f"https://api.unpaywall.org/v2/{doi}")
        curl.setopt(curl.WRITEFUNCTION, buffer.write)
        curl.setopt(curl.HEADERFUNCTION, lambda h: headers.update({h.decode().split(":")[0]: h.decode().split(":")[1].strip()}) if ":" in h.decode() else None)
        curl.perform()
        status_code = curl.getinfo(curl.RESPONSE_CODE)
        curl.close()

        body = buffer.getvalue().decode('utf-8')
        return PycurlResponse(status_code, headers, body)

    def download(self, doi, mode):
        """Download data using pycurl."""
        return self.get(doi)
