### Explanation of Changes
To migrate the code from using the `httpx` library to the `requests` library, the following changes were made:

1. **Import Statement**: Changed the import from `httpx` to `requests`.
2. **HTTP Request**: Replaced `httpx.get()` with `requests.get()`.
3. **Response Handling**: The response handling remains largely the same, but the `requests` library does not have a `status_code` attribute on the response object; instead, it uses the same attribute, so no change was needed there. The method to parse JSON remains the same as well.

Here is the modified code:

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