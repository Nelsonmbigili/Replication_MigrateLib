from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64
import hashlib
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

BS = 16
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS) 
unpad = lambda s: s[:-ord(s[len(s) - 1:])]


def dem_to_der(data):
    """
    ssh.PEM_cert_to_DER_cert seems to have issues with python3 bytes, so we wrap it
    """
    return data.encode('utf-8')


def encrypt_aes(key, raw):
    key = key.private_bytes(encoding=serialization.Encoding.DER, format=serialization.PrivateFormat.TraditionalOpenSSL)
    raw = pad(raw)
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    return base64.b64encode(iv + encryptor.update(raw.encode()) + encryptor.finalize())


def decrypt_aes(key, enc):
    enc = base64.b64decode(enc)
    iv = enc[:16]
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    decryptor = cipher.decryptor()
    return unpad(decryptor.update(enc[16:]) + decryptor.finalize()).decode()


def encrypt_rsa_oaep(privkey, data):
    if not isinstance(privkey, rsa.RSAPrivateKey):
        privkey = serialization.load_pem_private_key(privkey.encode(), password=None, backend=default_backend())
    ciphertext = privkey.encrypt(data, padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None))
    return ciphertext


def pubkey_from_dercert(der):
    cert = serialization.load_der_x509_certificate(der, default_backend())
    return cert.public_key()


def sign_sha256(key, data):
    if not isinstance(key, rsa.RSAPrivateKey):
        key = serialization.load_pem_private_key(key.encode(), password=None, backend=default_backend())
    signature = key.sign(data, padding.PSS(mgf=padding.MGF1(hashes.SHA256()), salt_length=padding.PSS.MAX_LENGTH), hashes.SHA256())
    return signature


def sign_sha1(key, data):
    if not isinstance(key, rsa.RSAPrivateKey):
        key = serialization.load_pem_private_key(key.encode(), password=None, backend=default_backend())
    signature = key.sign(data, padding.PKCS1v15(), hashes.SHA1())
    return signature


if __name__ == "__main__":
    from cryptography import x509
    # Convert from PEM to DER
    pem = open("../examples/server_cert.pem").read()
    der = dem_to_der(pem)
    rsa_pubkey = pubkey_from_dercert(der)
    priv_pem = open("../examples/mykey.pem").read()
    rsa_privkey = serialization.load_pem_private_key(priv_pem.encode(), password=None, backend=default_backend())
    cert = x509.load_pem_x509_certificate(pem.encode(), default_backend())

    print("Pub Key", rsa_pubkey)
    print("Priv Key", rsa_privkey)
    msg = encrypt_aes(rsa_privkey, "this is my message")
    print("Encrypted data: ", msg)
    from IPython import embed
    embed()
