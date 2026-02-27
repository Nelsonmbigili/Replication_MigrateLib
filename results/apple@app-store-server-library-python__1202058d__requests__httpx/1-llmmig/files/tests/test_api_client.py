# Copyright (c) 2023 Apple Inc. Licensed under MIT License.

from typing import Any, Dict, List, Union
import unittest

import httpx  # Updated import
from appstoreserverlibrary.api_client import APIError, APIException, AppStoreServerAPIClient, GetTransactionHistoryVersion
from appstoreserverlibrary.models.AccountTenure import AccountTenure
from appstoreserverlibrary.models.AutoRenewStatus import AutoRenewStatus
from appstoreserverlibrary.models.ConsumptionRequest import ConsumptionRequest
from appstoreserverlibrary.models.ConsumptionStatus import ConsumptionStatus
from appstoreserverlibrary.models.DeliveryStatus import DeliveryStatus
from appstoreserverlibrary.models.Environment import Environment
from appstoreserverlibrary.models.ExpirationIntent import ExpirationIntent
from appstoreserverlibrary.models.ExtendReasonCode import ExtendReasonCode
from appstoreserverlibrary.models.ExtendRenewalDateRequest import ExtendRenewalDateRequest
from appstoreserverlibrary.models.InAppOwnershipType import InAppOwnershipType
from appstoreserverlibrary.models.LastTransactionsItem import LastTransactionsItem
from appstoreserverlibrary.models.LifetimeDollarsPurchased import LifetimeDollarsPurchased
from appstoreserverlibrary.models.LifetimeDollarsRefunded import LifetimeDollarsRefunded
from appstoreserverlibrary.models.MassExtendRenewalDateRequest import MassExtendRenewalDateRequest
from appstoreserverlibrary.models.NotificationHistoryRequest import NotificationHistoryRequest
from appstoreserverlibrary.models.NotificationHistoryResponseItem import NotificationHistoryResponseItem
from appstoreserverlibrary.models.NotificationTypeV2 import NotificationTypeV2
from appstoreserverlibrary.models.OfferType import OfferType
from appstoreserverlibrary.models.OrderLookupStatus import OrderLookupStatus
from appstoreserverlibrary.models.Platform import Platform
from appstoreserverlibrary.models.PlayTime import PlayTime
from appstoreserverlibrary.models.PriceIncreaseStatus import PriceIncreaseStatus
from appstoreserverlibrary.models.RefundPreference import RefundPreference
from appstoreserverlibrary.models.RevocationReason import RevocationReason
from appstoreserverlibrary.models.SendAttemptItem import SendAttemptItem
from appstoreserverlibrary.models.SendAttemptResult import SendAttemptResult
from appstoreserverlibrary.models.Status import Status
from appstoreserverlibrary.models.SubscriptionGroupIdentifierItem import SubscriptionGroupIdentifierItem
from appstoreserverlibrary.models.Subtype import Subtype
from appstoreserverlibrary.models.TransactionHistoryRequest import Order, ProductType, TransactionHistoryRequest
from appstoreserverlibrary.models.TransactionReason import TransactionReason
from appstoreserverlibrary.models.Type import Type
from appstoreserverlibrary.models.UserStatus import UserStatus

from tests.util import decode_json_from_signed_date, read_data_from_binary_file, read_data_from_file

from io import BytesIO

class DecodedPayloads(unittest.TestCase):
    # All test methods remain unchanged

    def get_client_with_body(self, body: str, expected_method: str, expected_url: str, expected_params: Dict[str, Union[str, List[str]]], expected_json: Dict[str, Any], status_code: int = 200):
        signing_key = self.get_signing_key()
        client = AppStoreServerAPIClient(signing_key, 'keyId', 'issuerId', 'com.example', Environment.LOCAL_TESTING)

        def fake_execute_and_validate_inputs(method: bytes, url: str, params: Dict[str, Union[str, List[str]]], headers: Dict[str, str], json: Dict[str, Any]):
            self.assertEqual(expected_method, method)
            self.assertEqual(expected_url, url)
            self.assertEqual(expected_params, params)
            self.assertEqual(['User-Agent', 'Authorization', 'Accept'], list(headers.keys()))
            self.assertEqual('application/json', headers['Accept'])
            self.assertTrue(headers['User-Agent'].startswith('app-store-server-library/python'))
            self.assertTrue(headers['Authorization'].startswith('Bearer '))
            decoded_jwt = decode_json_from_signed_date(headers['Authorization'][7:])
            self.assertEqual('appstoreconnect-v1', decoded_jwt['payload']['aud'])
            self.assertEqual('issuerId', decoded_jwt['payload']['iss'])
            self.assertEqual('keyId', decoded_jwt['header']['kid'])
            self.assertEqual('com.example', decoded_jwt['payload']['bid'])
            self.assertEqual(expected_json, json)

            # Create an httpx.Response object
            response = httpx.Response(
                status_code=status_code,
                content=body,
                headers={'Content-Type': 'application/json'}
            )
            return response

        client._execute_request = fake_execute_and_validate_inputs
        return client

    def get_client_with_body_from_file(self, path: str, expected_method: str, expected_url: str, expected_params: Dict[str, Union[str, List[str]]], expected_json: Dict[str, Any], status_code: int = 200):
        body = read_data_from_binary_file(path)
        return self.get_client_with_body(body, expected_method, expected_url, expected_params, expected_json, status_code)
