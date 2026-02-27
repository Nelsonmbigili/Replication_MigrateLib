from decimal import Decimal
from typing import Dict, List
import json  # Added for JSON parsing with urllib3

import urllib3  # Replaced httpx with urllib3
from pydantic import BaseModel, Field

from dundie.settings import API_BASE_URL


class USDRate(BaseModel):
    code: str = Field(default="USD")
    codein: str = Field(default="USD")
    name: str = Field(default="Dolar/Dolar")
    value: Decimal = Field(alias="high")


def get_rates(currencies: List[str]) -> Dict[str, USDRate]:
    """Gets current rate for USD vs Currency"""
    return_data = {}
    http = urllib3.PoolManager()  # Create a PoolManager instance for making requests

    for currency in currencies:
        if currency == "USD":
            return_data[currency] = USDRate(high=1)
        else:
            response = http.request("GET", API_BASE_URL.format(currency=currency))
            if response.status == 200:  # Check the status code
                data = json.loads(response.data.decode("utf-8"))["USD" + currency]
                return_data[currency] = USDRate(**data)
            else:
                return_data[currency] = USDRate(name="api/error", high=0)

    return return_data
