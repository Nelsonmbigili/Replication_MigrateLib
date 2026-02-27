# Copyright (c) 2023 Apple Inc. Licensed under MIT License.

from Crypto.PublicKey import ECC
from Crypto.Signature import DSS
from Crypto.Hash import SHA256

import uuid
import base64

class PromotionalOfferSignatureCreator:
    _signing_key: ECC.EccKey
    _key_id: str
    _bundle_id: str
    def __init__(self, signing_key: bytes, key_id: str, bundle_id: str):
        self._signing_key = ECC.import_key(signing_key)
        self._key_id = key_id
        self._bundle_id = bundle_id
    def create_signature(self, product_identifier: str, subscription_offer_id: str, application_username: str, nonce: uuid.UUID, timestamp: int):
        """
        Return the Base64 encoded signature

        https://developer.apple.com/documentation/storekit/in-app_purchase/original_api_for_in-app_purchase/subscriptions_and_offers/generating_a_signature_for_promotional_offers

        :param product_identifier: The subscription product identifier
        :param subscription_offer_id: The subscription discount identifier
        :param application_username: An optional string value that you define; may be an empty string
        :param nonce: A one-time UUID value that your server generates. Generate a new nonce for every signature.
        :param timestamp: A timestamp your server generates in UNIX time format, in milliseconds. The timestamp keeps the offer active for 24 hours.
        :return: The Base64 encoded signature
        """
        payload = self._bundle_id + '\u2063' + \
            self._key_id + '\u2063' + \
            product_identifier + '\u2063' + \
            subscription_offer_id + '\u2063' + \
            application_username.lower()  + '\u2063'+ \
            str(nonce).lower() + '\u2063' + \
            str(timestamp)

        # Create a SHA256 hash of the payload
        hash_obj = SHA256.new(payload.encode('utf-8'))

        # Sign the hash using ECDSA
        signer = DSS.new(self._signing_key, 'fips-186-3')
        signature = signer.sign(hash_obj)

        # Return the Base64 encoded signature
        return base64.b64encode(signature).decode('utf-8')
