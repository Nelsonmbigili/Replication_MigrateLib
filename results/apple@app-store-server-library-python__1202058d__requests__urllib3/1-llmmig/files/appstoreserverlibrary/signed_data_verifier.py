# Copyright (c) 2023 Apple Inc. Licensed under MIT License.

from typing import List, Optional
from base64 import b64decode
from enum import IntEnum
import time
import datetime

import asn1
import jwt
import urllib3
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.ec import ECDSA
from cryptography.hazmat.primitives.hashes import SHA1, SHA256
from cryptography.x509 import ocsp, oid
from OpenSSL import crypto

from appstoreserverlibrary.models.AppTransaction import AppTransaction
from appstoreserverlibrary.models.LibraryUtility import _get_cattrs_converter

from .models.Environment import Environment
from .models.ResponseBodyV2DecodedPayload import ResponseBodyV2DecodedPayload
from .models.JWSTransactionDecodedPayload import JWSTransactionDecodedPayload
from .models.JWSRenewalInfoDecodedPayload import JWSRenewalInfoDecodedPayload

class SignedDataVerifier:
    """
    A class providing utility methods for verifying and decoding App Store signed data.
    """
    def __init__(
        self,
        root_certificates: List[bytes],
        enable_online_checks: bool,
        environment: Environment,
        bundle_id: str,
        app_apple_id: Optional[int] = None,
    ):
        self._chain_verifier = _ChainVerifier(root_certificates)
        self._environment = environment
        self._bundle_id = bundle_id
        self._app_apple_id = app_apple_id
        self._enable_online_checks = enable_online_checks
        if environment == Environment.PRODUCTION and app_apple_id is None:
            raise ValueError("appAppleId is required when the environment is Production")

    # Other methods remain unchanged...

    def check_ocsp_status(self, cert: crypto.X509, issuer: crypto.X509, root: crypto.X509):
        builder = ocsp.OCSPRequestBuilder()
        builder = builder.add_certificate(cert.to_cryptography(), issuer.to_cryptography(), SHA256())
        req = builder.build()
        authority_values = (
            cert.to_cryptography()
            .extensions.get_extension_for_oid(x509.oid.ExtensionOID.AUTHORITY_INFORMATION_ACCESS)
            .value
        )
        ocsps = [val for val in authority_values if val.access_method == x509.oid.AuthorityInformationAccessOID.OCSP]
        
        # Initialize urllib3 PoolManager
        http = urllib3.PoolManager()
        
        for o in ocsps:
            try:
                # Perform the POST request using urllib3
                response = http.request(
                    "POST",
                    o.access_location.value,
                    headers={"Content-Type": "application/ocsp-request"},
                    body=req.public_bytes(serialization.Encoding.DER),
                )
                
                if response.status == 200:
                    ocsp_resp = ocsp.load_der_ocsp_response(response.data)
                    if ocsp_resp.response_status == ocsp.OCSPResponseStatus.SUCCESSFUL:
                        certs = [issuer]
                        for ocsp_cert in ocsp_resp.certificates:
                            certs.append(crypto.X509.from_cryptography(ocsp_cert))
                        # Find signing cert
                        signing_cert = None
                        for potential_signing_cert in certs:
                            if ocsp_resp.responder_key_hash:
                                subject_public_key_info = (
                                    potential_signing_cert.get_pubkey()
                                    .to_cryptography_key()
                                    .public_bytes(
                                        encoding=serialization.Encoding.DER,
                                        format=serialization.PublicFormat.SubjectPublicKeyInfo,
                                    )
                                )
                                decoder = asn1.Decoder()
                                decoder.start(subject_public_key_info)
                                decoder.enter()
                                decoder.read()
                                _, value = decoder.read()
                                digest = hashes.Hash(SHA1())
                                digest.update(value)
                                if digest.finalize() == ocsp_resp.responder_key_hash:
                                    signing_cert = potential_signing_cert
                                    break

                            elif ocsp_resp.responder_name:
                                if ocsp_resp.responder_name == potential_signing_cert.subject.rfc4514_string():
                                    signing_cert = potential_signing_cert
                                    break
                        if signing_cert is None:
                            raise VerificationException(VerificationStatus.VERIFICATION_FAILURE)

                        if signing_cert.to_cryptography().public_bytes(
                            encoding=serialization.Encoding.DER
                        ) == issuer.to_cryptography().public_bytes(encoding=serialization.Encoding.DER):
                            # We trust this because it is the issuer
                            pass
                        else:
                            trusted_store = crypto.X509Store()
                            trusted_store.add_cert(issuer)
                            trusted_store.add_cert(root)  # Apparently a full chain is always needed
                            verification_context = crypto.X509StoreContext(trusted_store, signing_cert, [])
                            verification_context.verify_certificate()
                            if (
                                oid.ExtendedKeyUsageOID.OCSP_SIGNING
                                not in signing_cert.to_cryptography()
                                .extensions.get_extension_for_class(x509.ExtendedKeyUsage)
                                .value._usages
                            ):
                                raise VerificationException(VerificationStatus.VERIFICATION_FAILURE)

                        # Confirm response is signed by signing_certificate
                        signing_cert.to_cryptography().public_key().verify(
                            ocsp_resp.signature, ocsp_resp.tbs_response_bytes, ECDSA(ocsp_resp.signature_hash_algorithm)
                        )

                        # Get the CertId
                        for single_response in ocsp_resp.responses:
                            # Get the cert ID with the provided hashing algorithm (using the request builder wrapper)
                            builder = ocsp.OCSPRequestBuilder()
                            builder = builder.add_certificate(
                                cert.to_cryptography(), issuer.to_cryptography(), single_response.hash_algorithm
                            )
                            req = builder.build()
                            if (
                                single_response.certificate_status == ocsp.OCSPCertStatus.GOOD
                                and single_response.serial_number == req.serial_number
                                and single_response.issuer_key_hash == req.issuer_key_hash
                                and single_response.issuer_name_hash == req.issuer_name_hash
                            ):
                                # Success
                                return

            except urllib3.exceptions.HTTPError as e:
                raise VerificationException(VerificationStatus.VERIFICATION_FAILURE) from e

        raise VerificationException(VerificationStatus.VERIFICATION_FAILURE)


class VerificationStatus(IntEnum):
    OK = 0
    VERIFICATION_FAILURE = 1
    INVALID_APP_IDENTIFIER = 2
    INVALID_CERTIFICATE = 3
    INVALID_CHAIN_LENGTH = 4
    INVALID_CHAIN = 5
    INVALID_ENVIRONMENT = 6


class VerificationException(Exception):
    def __init__(self, status: VerificationStatus):
        super().__init__("Verification failed with status " + status.name)
        self.status = status
