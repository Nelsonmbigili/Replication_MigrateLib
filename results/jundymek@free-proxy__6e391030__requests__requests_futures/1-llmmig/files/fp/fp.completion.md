### Explanation of Changes
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created a `FuturesSession` object to handle asynchronous requests.
3. **Request Method Changes**: Replaced `requests.get` with `session.get` to use the `FuturesSession` object for making asynchronous requests.
4. **Response Handling**: Since `requests_futures` returns a `Future` object, the `.result()` method is used to retrieve the actual response object where necessary.

These changes ensure that the code now uses `requests_futures` for asynchronous HTTP requests while maintaining the original functionality.

---

### Modified Code
```python
#!/usr/bin/env python3

import random

import lxml.html as lh
from requests_futures.sessions import FuturesSession

from fp.errors import FreeProxyException


class FreeProxy:
    '''
    FreeProxy class scrapes proxies from <https://www.sslproxies.org/>,
    <https://www.us-proxy.org/>, <https://free-proxy-list.net/uk-proxy.html>,
    and <https://free-proxy-list.net> and checks if proxy is working. 
    There is possibility to filter proxies by country and acceptable timeout. 
    You can also randomize list of proxies from where script would get first 
    working proxy.
    '''

    def __init__(self, country_id=None, timeout=0.5, rand=False, anonym=False, elite=False, google=None, https=False, url='https://www.google.com'):
        self.country_id = country_id
        self.timeout = timeout
        self.random = rand
        self.anonym = anonym
        self.elite = elite
        self.google = google
        self.schema = 'https' if https else 'http'
        self.url = url
        self.session = FuturesSession()  # Initialize FuturesSession for async requests

    def get_proxy_list(self, repeat):
        try:
            future = self.session.get(self.__website(repeat))  # Asynchronous GET request
            page = future.result()  # Wait for the response
            doc = lh.fromstring(page.content)
        except Exception as e:
            raise FreeProxyException(
                f'Request to {self.__website(repeat)} failed') from e
        try:
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            return [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}'
                    for i in range(1, len(tr_elements)) if self.__criteria(tr_elements[i])]
        except Exception as e:
            raise FreeProxyException('Failed to get list of proxies') from e

    def __website(self, repeat):
        if repeat:
            return "https://free-proxy-list.net"
        elif self.country_id == ['US']:
            return 'https://www.us-proxy.org'
        elif self.country_id == ['GB']:
            return 'https://free-proxy-list.net/uk-proxy.html'
        else:
            return 'https://www.sslproxies.org'

    def __criteria(self, row_elements):
        country_criteria = True if not self.country_id else row_elements[2].text_content(
        ) in self.country_id
        elite_criteria = True if not self.elite else 'elite' in row_elements[4].text_content(
        )
        anonym_criteria = True if (
            not self.anonym) or self.elite else 'anonymous' == row_elements[4].text_content()
        switch = {'yes': True, 'no': False}
        google_criteria = True if self.google is None else self.google == switch.get(
            row_elements[5].text_content())
        https_criteria = True if self.schema == 'http' else row_elements[6].text_content(
        ).lower() == 'yes'
        return country_criteria and elite_criteria and anonym_criteria and google_criteria and https_criteria

    def get(self, repeat=False):
        '''Returns a working proxy that matches the specified parameters.'''
        proxy_list = self.get_proxy_list(repeat)
        if self.random:
            random.shuffle(proxy_list)
        working_proxy = None
        for proxy_address in proxy_list:
            proxies = {self.schema: f'http://{proxy_address}'}
            try:
                working_proxy = self.__check_if_proxy_is_working(proxies)
                if working_proxy:
                    return working_proxy
            except Exception:
                continue
        if not working_proxy and not repeat:
            if self.country_id is not None:
                self.country_id = None
            return self.get(repeat=True)
        raise FreeProxyException(
            'There are no working proxies at this time.')

    def __check_if_proxy_is_working(self, proxies):
        url = f'{self.schema}://{self.url}'
        ip = proxies[self.schema].split(':')[1][2:]
        future = self.session.get(url, proxies=proxies, timeout=self.timeout, stream=True)  # Asynchronous GET request
        with future.result() as r:  # Wait for the response and process it
            if r.raw.connection.sock and r.raw.connection.sock.getpeername()[0] == ip:
                return proxies[self.schema]
        return
```

---

### Summary of Changes
- Replaced `requests.get` with `session.get` using a `FuturesSession` object.
- Used `.result()` to retrieve the response from the `Future` object returned by `session.get`.
- Ensured all asynchronous requests are properly handled without altering the original logic or structure of the code.