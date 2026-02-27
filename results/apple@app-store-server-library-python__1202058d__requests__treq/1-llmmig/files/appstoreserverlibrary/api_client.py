# Copyright (c) 2023 Apple Inc. Licensed under MIT License.

import calendar
import datetime
from enum import IntEnum, Enum
from typing import Any, Dict, List, MutableMapping, Optional, Type, TypeVar, Union
from attr import define
import treq

import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from appstoreserverlibrary.models.LibraryUtility import _get_cattrs_converter
from .models.CheckTestNotificationResponse import CheckTestNotificationResponse
from .models.ConsumptionRequest import ConsumptionRequest

from .models.Environment import Environment
from .models.ExtendRenewalDateRequest import ExtendRenewalDateRequest
from .models.ExtendRenewalDateResponse import ExtendRenewalDateResponse
from .models.HistoryResponse import HistoryResponse
from .models.MassExtendRenewalDateRequest import MassExtendRenewalDateRequest
from .models.MassExtendRenewalDateResponse import MassExtendRenewalDateResponse
from .models.MassExtendRenewalDateStatusResponse import MassExtendRenewalDateStatusResponse
from .models.NotificationHistoryRequest import NotificationHistoryRequest
from .models.NotificationHistoryResponse import NotificationHistoryResponse
from .models.OrderLookupResponse import OrderLookupResponse
from .models.RefundHistoryResponse import RefundHistoryResponse
from .models.SendTestNotificationResponse import SendTestNotificationResponse
from .models.Status import Status
from .models.StatusResponse import StatusResponse
from .models.TransactionHistoryRequest import TransactionHistoryRequest
from .models.TransactionInfoResponse import TransactionInfoResponse

T = TypeVar('T')

# (APIError and APIException classes remain unchanged)

class BaseAppStoreServerAPIClient:
    def __init__(self, signing_key: bytes, key_id: str, issuer_id: str, bundle_id: str, environment: Environment):
        if environment == Environment.XCODE:
            raise ValueError("Xcode is not a supported environment for an AppStoreServerAPIClient")
        if environment == Environment.PRODUCTION:
            self._base_url = "https://api.storekit.itunes.apple.com"
        elif environment == Environment.LOCAL_TESTING:
            self._base_url = "https://local-testing-base-url"
        else:
            self._base_url = "https://api.storekit-sandbox.itunes.apple.com"
        self._signing_key = serialization.load_pem_private_key(signing_key, password=None, backend=default_backend())
        self._key_id = key_id
        self._issuer_id = issuer_id
        self._bundle_id = bundle_id

    def _generate_token(self) -> str:
        future_time = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=5)
        return jwt.encode(
            {
                "bid": self._bundle_id,
                "iss": self._issuer_id,
                "aud": "appstoreconnect-v1",
                "exp": calendar.timegm(future_time.timetuple()),
            },
            self._signing_key,
            algorithm="ES256",
            headers={"kid": self._key_id},
        )
    
    def _get_full_url(self, path) -> str:
        return self._base_url + path
    
    def _get_headers(self) -> Dict[str, str]:
        return {
            'User-Agent': "app-store-server-library/python/1.5.0",
            'Authorization': 'Bearer ' + self._generate_token(),
            'Accept': 'application/json'
        }
    
    def _get_request_json(self, body) -> Dict[str, Any]:
        c = _get_cattrs_converter(type(body)) if body is not None else None
        return c.unstructure(body) if body is not None else None

    def _parse_response(self, status_code: int, headers: MutableMapping, json_supplier, destination_class: Type[T]) -> T:
        if 200 <= status_code < 300:
            if destination_class is None:
                return
            c = _get_cattrs_converter(destination_class)
            response_body = json_supplier()
            return c.structure(response_body, destination_class)
        else:
            # Best effort parsing of the response body
            if not 'content-type' in headers or headers['content-type'] != 'application/json':
                raise APIException(status_code)
            try:
                response_body = json_supplier()
                raise APIException(status_code, response_body['errorCode'], response_body['errorMessage'])
            except APIException as e:
                raise e
            except Exception as e:
                raise APIException(status_code) from e


class AppStoreServerAPIClient(BaseAppStoreServerAPIClient):
    def __init__(self, signing_key: bytes, key_id: str, issuer_id: str, bundle_id: str, environment: Environment):
        super().__init__(signing_key=signing_key, key_id=key_id, issuer_id=issuer_id, bundle_id=bundle_id, environment=environment)
    
    def _make_request(self, path: str, method: str, queryParameters: Dict[str, Union[str, List[str]]], body, destination_class: Type[T]) -> T:
        url = self._get_full_url(path)
        json = self._get_request_json(body)
        headers = self._get_headers()
        
        response = self._execute_request(method, url, queryParameters, headers, json)
        return self._parse_response(response.code, response.headers, lambda: response.json(), destination_class)

    def _execute_request(self, method: str, url: str, params: Dict[str, Union[str, List[str]]], headers: Dict[str, str], json: Dict[str, Any]):
        return treq.request(method, url, params=params, headers=headers, json=json)


class AsyncAppStoreServerAPIClient(BaseAppStoreServerAPIClient):
    def __init__(self, signing_key: bytes, key_id: str, issuer_id: str, bundle_id: str, environment: Environment):
        super().__init__(signing_key=signing_key, key_id=key_id, issuer_id=issuer_id, bundle_id=bundle_id, environment=environment)

    async def _make_request(self, path: str, method: str, queryParameters: Dict[str, Union[str, List[str]]], body, destination_class: Type[T]) -> T:
        url = self._get_full_url(path)
        json = self._get_request_json(body)
        headers = self._get_headers()
        
        response = await self._execute_request(method, url, queryParameters, headers, json)
        return self._parse_response(response.code, response.headers, lambda: response.json(), destination_class)

    async def _execute_request(self, method: str, url: str, params: Dict[str, Union[str, List[str]]], headers: Dict[str, str], json: Dict[str, Any]):
        return await treq.request(method, url, params=params, headers=headers, json=json)
