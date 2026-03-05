from Crypto.PublicKey import RSA
from OpenSSL.crypto import load_certificate, FILETYPE_PEM, X509


def pem_cert_bytes_to_open_ssl_x509(cert: bytes) -> X509:
    """Convert PEM-formatted certificate bytes into an X509 instance usable for cert
    chain validation
    """
    cert_openssl = load_certificate(FILETYPE_PEM, cert)
    return cert_openssl
