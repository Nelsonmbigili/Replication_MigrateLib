### Explanation of Changes
To migrate the code from using the `httpx` library to the `aiohttp` library, the following changes were made:

1. **Import Statement**: Changed the import from `httpx` to `aiohttp`.
2. **Asynchronous Function**: The `get_rates` function was modified to be asynchronous (`async def`) to accommodate the asynchronous nature of `aiohttp`.
3. **Session Management**: Introduced an `aiohttp.ClientSession` to manage HTTP requests, which is necessary for making requests with `aiohttp`.
4. **Awaiting Requests**: Used `await` with the `session.get()` method to make the HTTP request asynchronously.
5. **Response Handling**: The response handling remains similar, but we now await the response and use `await response.json()` to parse the JSON data.

Here is the modified code:

```python
from decimal import Decimal
from typing import Dict, List

import aiohttp
from pydantic import BaseModel, Field

from dundie.settings import API_BASE_URL


class USDRate(BaseModel):
    code: str = Field(default="USD")
    codein: str = Field(default="USD")
    name: str = Field(default="Dolar/Dolar")
    value: Decimal = Field(alias="high")


async def get_rates(currencies: List[str]) -> Dict[str, USDRate]:
    """Gets current rate for USD vs Currency"""
    return_data = {}
    async with aiohttp.ClientSession() as session:
        for currency in currencies:
            if currency == "USD":
                return_data[currency] = USDRate(high=1)
            else:
                async with session.get(API_BASE_URL.format(currency=currency)) as response:
                    if response.status == 200:
                        data = await response.json()
                        return_data[currency] = USDRate(**data["USD" + currency])
                    else:
                        return_data[currency] = USDRate(name="api/error", high=0)

    return return_data
```