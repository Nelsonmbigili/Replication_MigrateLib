### Explanation of Changes
To migrate the code from using the `beautifulsoup4` library to the `pyquery` library, the following changes were made:

1. **Import Statement**: The import statement for `BeautifulSoup` was replaced with an import for `PyQuery` from the `pyquery` library.
2. **Soup Creation**: The function `soup_from_str` was modified to create a `PyQuery` object instead of a `BeautifulSoup` object. The `PyQuery` constructor can directly take the HTML content as a string.
3. **Return Value**: The return type of `soup_from_str` was changed to return a `PyQuery` object.

Here is the modified code:

```python
from pyquery import PyQuery as pq
from django.http import QueryDict
from django.test.client import MULTIPART_CONTENT, Client


def get_soup(response):
    content = response.content
    return soup_from_str(content)


def soup_from_str(content):
    soup = pq(content)
    return soup


def put_request_as_querystring(client, url, data):
    """
    for some reason,
    htmx sends PUT requests as querystings??
    """
    qs = QueryDict(mutable=True)
    for k, v in data.items():
        if isinstance(v, list):
            qs.setlist(k, v)
        else:
            qs.update({k: v})

    query_string = qs.urlencode()
    response = client.put(url, data=query_string)
    return response
```