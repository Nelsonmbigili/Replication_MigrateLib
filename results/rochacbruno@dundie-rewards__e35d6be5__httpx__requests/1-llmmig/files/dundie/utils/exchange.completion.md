### Explanation of Changes:
To migrate the code from using the `httpx` library to the `requests` library, the following changes were made:
1. Replaced the `httpx.get` method with `requests.get`.
2. Updated the import statement to import `requests` instead of `httpx`.
3. The behavior of `requests.get` is similar to `httpx.get`, so no additional changes were required for handling the response or status codes.

### Modified Code:
```python
from decimal import Decimal
from typing import Dict, List

import requests
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
    for currency in currencies:
        if currency == "USD":
            return_data[currency] = USDRate(high=1)
        else:
            response = requests.get(API_BASE_URL.format(currency=currency))
            if response.status_code == 200:
                data = response.json()["USD" + currency]
                return_data[currency] = USDRate(**data)
            else:
                return_data[currency] = USDRate(name="api/error", high=0)

    return return_data
```