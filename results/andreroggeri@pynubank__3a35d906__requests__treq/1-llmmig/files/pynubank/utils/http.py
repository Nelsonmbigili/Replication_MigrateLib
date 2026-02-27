import treq
from OpenSSL import crypto
from twisted.internet.ssl import CertificateOptions
from twisted.internet.defer import ensureDeferred

from pynubank import NuRequestException


class HttpClient:

    def __init__(self):
        self._cert = None
        self._headers = {
            'Content-Type': 'application/json',
            'X-Correlation-Id': 'and-7-86-2-1000005524.9twu3pgr',
            'User-Agent': 'pynubank Client - https://github.com/andreroggeri/pynubank',
        }

    def set_cert_data(self, cert_data: bytes):
        self._cert = cert_data

    def set_header(self, name: str, value: str):
        self._headers[name] = value

    def remove_header(self, name: str):
        self._headers.pop(name)

    def get_header(self, name: str):
        return self._headers.get(name)

    @property
    def _cert_args(self):
        if not self._cert:
            return {}

        # Load the PKCS#12 certificate
        pkcs12 = crypto.load_pkcs12(self._cert, b'')
        private_key = pkcs12.get_privatekey()
        certificate = pkcs12.get_certificate()
        additional_certs = pkcs12.get_ca_certificates() or []

        # Create an SSLContext using the certificate and private key
        context = CertificateOptions(
            privateKey=crypto.dump_privatekey(crypto.FILETYPE_PEM, private_key),
            certificate=crypto.dump_certificate(crypto.FILETYPE_PEM, certificate),
            extraCertChain=[
                crypto.dump_certificate(crypto.FILETYPE_PEM, cert)
                for cert in additional_certs
            ]
        )
        return {'context': context}

    async def _handle_response(self, response) -> dict:
        if response.code != 200:
            body = await response.text()
            raise NuRequestException(f"HTTP {response.code}: {body}")

        return await response.json()

    async def raw_get(self, url: str):
        return await treq.get(url, headers=self._headers, **self._cert_args)

    async def raw_post(self, url: str, json: dict):
        return await treq.post(url, json=json, headers=self._headers, **self._cert_args)

    async def get(self, url: str) -> dict:
        response = await self.raw_get(url)
        return await self._handle_response(response)

    async def post(self, url: str, json: dict) -> dict:
        response = await self.raw_post(url, json)
        return await self._handle_response(response)
