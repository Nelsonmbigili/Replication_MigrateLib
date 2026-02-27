from Crypto.PublicKey import RSA


def pem_cert_bytes_to_open_ssl_x509(cert: bytes):
    """Convert PEM-formatted certificate bytes into an RSA public key instance."""
    try:
        cert_key = RSA.import_key(cert)
        return cert_key
    except ValueError as e:
        raise ValueError("Invalid PEM certificate format") from e
