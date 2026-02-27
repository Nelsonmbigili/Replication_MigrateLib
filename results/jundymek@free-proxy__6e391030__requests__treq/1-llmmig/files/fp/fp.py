#!/usr/bin/env python3

import random
from twisted.internet import reactor
from twisted.internet.defer import inlineCallbacks, returnValue
from twisted.internet.endpoints import HostnameEndpoint
import lxml.html as lh
import treq

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

    @inlineCallbacks
    def get_proxy_list(self, repeat):
        try:
            response = yield treq.get(self.__website(repeat), timeout=self.timeout)
            content = yield response.content()
            doc = lh.fromstring(content)
        except Exception as e:
            raise FreeProxyException(
                f'Request to {self.__website(repeat)} failed') from e
        try:
            tr_elements = doc.xpath('//*[@id="list"]//tr')
            proxy_list = [f'{tr_elements[i][0].text_content()}:{tr_elements[i][1].text_content()}'
                          for i in range(1, len(tr_elements)) if self.__criteria(tr_elements[i])]
            returnValue(proxy_list)
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

    @inlineCallbacks
    def get(self, repeat=False):
        '''Returns a working proxy that matches the specified parameters.'''
        proxy_list = yield self.get_proxy_list(repeat)
        if self.random:
            random.shuffle(proxy_list)
        working_proxy = None
        for proxy_address in proxy_list:
            proxies = {self.schema: f'http://{proxy_address}'}
            try:
                working_proxy = yield self.__check_if_proxy_is_working(proxies)
                if working_proxy:
                    returnValue(working_proxy)
            except Exception:
                continue
        if not working_proxy and not repeat:
            if self.country_id is not None:
                self.country_id = None
            returnValue((yield self.get(repeat=True)))
        raise FreeProxyException(
            'There are no working proxies at this time.')

    @inlineCallbacks
    def __check_if_proxy_is_working(self, proxies):
        url = f'{self.schema}://{self.url}'
        proxy_address = proxies[self.schema]
        host, port = proxy_address.split(':')[1][2:], int(proxy_address.split(':')[2])
        endpoint = HostnameEndpoint(reactor, host, port)
        try:
            response = yield treq.get(url, timeout=self.timeout, proxy=endpoint)
            if response.code == 200:
                returnValue(proxies[self.schema])
        except Exception:
            returnValue(None)
