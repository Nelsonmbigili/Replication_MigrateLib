#!/usr/bin/env python3

import random
import pycurl
import io
import lxml.html as lh

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

    def get_proxy_list(self, repeat):
        try:
            response_buffer = io.BytesIO()
            curl = pycurl.Curl()
            curl.setopt(pycurl.URL, self.__website(repeat))
            curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
            curl.setopt(pycurl.TIMEOUT, int(self.timeout))
            curl.perform()
            curl.close()

            page_content = response_buffer.getvalue().decode('utf-8')
            doc = lh.fromstring(page_content)
        except pycurl.error as e:
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
            except pycurl.error:
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

        response_buffer = io.BytesIO()
        curl = pycurl.Curl()
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.PROXY, proxies[self.schema])
        curl.setopt(pycurl.TIMEOUT, int(self.timeout))
        curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)

        try:
            curl.perform()
            peer_ip = curl.getinfo(pycurl.PRIMARY_IP)
            curl.close()
            if peer_ip == ip:
                return proxies[self.schema]
        except pycurl.error:
            curl.close()
            return
        return
