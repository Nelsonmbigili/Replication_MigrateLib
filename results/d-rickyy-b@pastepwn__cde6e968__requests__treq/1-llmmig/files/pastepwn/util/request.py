import logging
from threading import Lock

import treq
from twisted.internet import reactor, defer
from twisted.internet.defer import inlineCallbacks, returnValue


class Request:
    _instance = None
    _initialized = False
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        # override method to implement singleton
        # source: http://alacret.blogspot.com/2015/04/python-thread-safe-singleton-pattern.html
        if Request._instance is None:
            with Request._lock:
                if Request._instance is None:
                    Request._instance = super().__new__(cls)
        return Request._instance

    def __init__(self, proxies=None, headers=None):
        if not self._initialized:
            self.logger = logging.getLogger(__name__)
            self.proxies = proxies  # Note: treq does not natively support proxies
            self.headers = headers
            self.logger.info("Using the following custom proxies: %s", proxies)
            self.logger.info("Using the following system proxies: %s", "Not supported in treq")
            Request._initialized = True

    @inlineCallbacks
    def _request_wrapper(self, method, url, data=None, timeout=5, **kwargs):
        headers = {"User-Agent": "pastepwn (https://github.com/d-Rickyy-b/pastepwn)"}

        if self.headers is not None:
            headers.update(self.headers)

        try:
            response = yield treq.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                timeout=timeout,
                **kwargs
            )
            content = yield treq.content(response)
            returnValue(content.decode("utf-8"))
        except Exception as e:
            self.logger.warning("Error while requesting %s: %s", url, str(e))
            returnValue("")

    def get(self, url, data=None, timeout=5):
        return self._request_wrapper(method="GET", url=url, data=data, timeout=timeout)

    def post(self, url, data=None, timeout=5):
        return self._request_wrapper(method="POST", url=url, data=data, timeout=timeout)

    def put(self, url, data=None, timeout=5):
        return self._request_wrapper(method="PUT", url=url, data=data, timeout=timeout)

    def delete(self, url, data=None, timeout=5):
        return self._request_wrapper(method="DELETE", url=url, data=data, timeout=timeout)


# Example usage (requires Twisted reactor to run):
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    @inlineCallbacks
    def main():
        req = Request()
        response = yield req.get("https://httpbin.org/get")
        print(response)

    reactor.callWhenRunning(main)
    reactor.run()
