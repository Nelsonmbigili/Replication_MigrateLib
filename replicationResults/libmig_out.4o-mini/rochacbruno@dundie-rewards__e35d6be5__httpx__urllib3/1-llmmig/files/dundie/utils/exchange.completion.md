### Explanation of Changes
To migrate the code from using the `httpx` library to the `urllib3` library, the following changes were made:

1. **Import Statement**: The import for `httpx` was replaced with `urllib3`.
2. **HTTP Client Initialization**: An instance of `urllib3.PoolManager` was created to manage connections.
3. **Making Requests**: The `httpx.get` method was replaced with `http.client.request` method from `urllib3`, which requires specifying the HTTP method and the URL.
4. **Response Handling**: The response from `urllib3` is handled differently. Instead of accessing `response.status_code`, we check the response status using `response.status`. The JSON data is accessed using `response.data` and then decoded.

Here is the modified code:

```python
from decimal import Decimal
from typing import Dict, List

import urllib3
import json
from pydantic import BaseModel, Field

from dundie.settings import API_BASE_URL

http = urllib3.PoolManager()

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
            response = http.request('GET', API_BASE_URL.format(currency=currency))
            if response.status == 200:
                data = json.loads(response.data.decode('utf-8'))["USD" + currency]
                return_data[currency] = USDRate(**data)
            else:
                return_data[currency] = USDRate(name="api/error", high=0)

    return return_data
```