### Explanation of Changes
To migrate the code from using the `requests` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import statement for `requests` was replaced with `urllib3`. 
2. **Creating a Pool Manager**: `urllib3` requires a `PoolManager` to handle connections, so an instance of `PoolManager` was created.
3. **Making Requests**: The `requests.post` method was replaced with `http.request('POST', ...)` to send POST requests.
4. **Handling Response**: The response from `urllib3` is different from `requests`, so the way to access the response data and headers was adjusted accordingly.

Here is the modified code:

```python
import pytest
import responses
import urllib3

from filestack import __version__

TEST_URL = 'http://just.some.url/'
http = urllib3.PoolManager()

@responses.activate
def test_req_wrapper_overwrite_headers():
    responses.add(responses.POST, TEST_URL)
    response = http.request('POST', TEST_URL)
    assert response.url == TEST_URL
    assert 'Filestack-Trace-Id' in response.headers
    assert 'Filestack-Trace-Span' in response.headers
    assert 'filestack-python {}'.format(__version__) == response.headers['User-Agent']
    assert 'Python-{}'.format(__version__) == response.headers['Filestack-Source']


@responses.activate
def test_req_wrapper_use_provided_headers():
    responses.add(responses.POST, TEST_URL)
    custom_headers = {'something': 'used explicitly'}
    response = http.request('POST', TEST_URL, headers=custom_headers)
    print(response.headers)
    assert response.url == TEST_URL
    assert response.headers['something'] == 'used explicitly'


@responses.activate
def test_req_wrapper_raise_exception():
    responses.add(responses.POST, TEST_URL, status=500, body=b'oops!')
    with pytest.raises(Exception, match='oops!'):
        http.request('POST', TEST_URL)
``` 

This code now uses `urllib3` for making HTTP requests while maintaining the original structure and functionality of the tests.