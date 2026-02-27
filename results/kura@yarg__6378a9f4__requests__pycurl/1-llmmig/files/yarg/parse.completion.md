### Explanation of Changes
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get`**: The `requests.get` function was replaced with `pycurl` to perform HTTP GET requests. `pycurl` requires setting up a `pycurl.Curl` object, configuring it with the URL, and capturing the response using a `BytesIO` buffer.
2. **Response Handling**: Since `pycurl` does not return a response object like `requests`, the HTTP status code and response content were manually extracted using `pycurl` options (`CURLINFO_RESPONSE_CODE` for status code and a `BytesIO` buffer for content).
3. **Error Handling**: Added error handling for `pycurl` using `pycurl.error` to raise an `HTTPError` if the request fails or the status code is 300 or higher.
4. **Removed `requests` Import**: The `requests` library import was removed since it is no longer used.

Below is the modified code:

---

### Modified Code
```python
# -*- coding: utf-8 -*-

# (The MIT License)
#
# Copyright (c) 2014 Kura
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the 'Software'), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED 'AS IS', WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from datetime import datetime
import xml.etree.ElementTree
import pycurl
from io import BytesIO

from .exceptions import HTTPError


def _get(pypi_server):
    """
    Query the PyPI RSS feed and return a list
    of XML items.
    """
    buffer = BytesIO()
    curl = pycurl.Curl()
    curl.setopt(pycurl.URL, pypi_server)
    curl.setopt(pycurl.WRITEDATA, buffer)
    curl.setopt(pycurl.FOLLOWLOCATION, True)

    try:
        curl.perform()
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)
        if status_code >= 300:
            raise HTTPError(status_code=status_code, reason="HTTP Error")
    except pycurl.error as e:
        raise HTTPError(status_code=0, reason=str(e))
    finally:
        curl.close()

    response_content = buffer.getvalue()
    if hasattr(response_content, 'decode'):
        tree = xml.etree.ElementTree.fromstring(response_content.decode())
    else:
        tree = xml.etree.ElementTree.fromstring(response_content)
    channel = tree.find('channel')
    return channel.findall('item')


def newest_packages(
        pypi_server="https://pypi.python.org/pypi?%3Aaction=packages_rss"):
    """
    Constructs a request to the PyPI server and returns a list of
    :class:`yarg.parse.Package`.

    :param pypi_server: (option) URL to the PyPI server.

        >>> import yarg
        >>> yarg.newest_packages()
        [<Package yarg>, <Package gray>, <Package ragy>]
    """
    items = _get(pypi_server)
    i = []
    for item in items:
        i_dict = {'name': item[0].text.split()[0],
                  'url': item[1].text,
                  'description': item[3].text,
                  'date': item[4].text}
        i.append(Package(i_dict))
    return i


def latest_updated_packages(
        pypi_server="https://pypi.python.org/pypi?%3Aaction=rss"):
    """
    Constructs a request to the PyPI server and returns a list of
    :class:`yarg.parse.Package`.

    :param pypi_server: (option) URL to the PyPI server.

        >>> import yarg
        >>> yarg.latest_updated_packages()
        [<Package yarg>, <Package gray>, <Package ragy>]
    """
    items = _get(pypi_server)
    i = []
    for item in items:
        name, version = item[0].text.split()
        i_dict = {'name': name,
                  'version': version,
                  'url': item[1].text,
                  'description': item[2].text,
                  'date': item[3].text}
        i.append(Package(i_dict))
    return i


class Package(object):
    """
    A PyPI package generated from the RSS feed information.

    :param pypi_dict: A dictionary retrieved from the PyPI server.
    """

    def __init__(self, pypi_dict):
        self._content = pypi_dict

    def __repr__(self):
        return "<Package {0}>".format(self.name)

    @property
    def name(self):
        """
            >>> package = yarg.newest_packages()[0]
            >>> package.name
            'yarg'
            >>> package = yarg.latest_updated_packages()[0]
            >>> package.name
            'yarg'
        """
        return self._content['name']

    @property
    def version(self):
        """
            >>> package = yarg.newest_packages()[0]
            >>> package.name
            'yarg'
            >>> package = yarg.latest_updated_packages()[0]
            >>> package.name
            'yarg'
        """
        if 'version' not in self._content:
            return None
        return self._content['version']

    @property
    def url(self):
        """
        This is only available for :meth:`yarg.latest_updated_packages`, for
        :meth:`yarg.newest_packages` will return `None`

            >>> package = yarg.latest_updated_packages()[0]
            >>> package.url
            'http://pypi.python.org/pypi/yarg'
        """
        return self._content['url']

    @property
    def date(self):
        """
            >>> package = yarg.newest_packages()[0]
            >>> package.date
            datetime.datetime(2014, 8, 9, 8, 40, 20)
            >>> package = yarg.latest_updated_packages()[0]
            >>> package.date
            datetime.datetime(2014, 8, 9, 8, 40, 20)
        """
        return datetime.strptime(self._content['date'],
                                 "%d %b %Y %H:%M:%S %Z")

    @property
    def description(self):
        """
            >>> package = yarg.newest_packages()[0]
            >>> package.description
            'Some random summary stuff'
            >>> package = yarg.latest_updated_packages()[0]
            >>> package.description
            'Some random summary stuff'
        """
        return self._content['description']
```