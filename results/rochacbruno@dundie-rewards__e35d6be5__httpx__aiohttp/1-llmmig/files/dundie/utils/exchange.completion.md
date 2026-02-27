### Explanation of Changes
To migrate the code from `httpx` to `aiohttp`, the following changes were made:
1. Replaced the synchronous `httpx.get` call with an asynchronous `aiohttp.ClientSession` and its `get` method.
2. Updated the function `get_rates` to be asynchronous (`async def`) since `aiohttp` is an asynchronous library.
3. Used `async with` to manage the lifecycle of the `aiohttp.ClientSession` and the HTTP request.
4. Updated the response handling to use `await` for asynchronous operations like `response.json()`.

### Modified Code
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

### Key Points
- The `get_rates` function is now asynchronous (`async def`) to accommodate the asynchronous nature of `aiohttp`.
- `aiohttp.ClientSession` is used with `async with` to ensure proper resource cleanup.
- The `response.json()` method is awaited (`await response.json()`) because it is an asynchronous operation in `aiohttp`.
- The `response.status` attribute is used instead of `response.status_code` to check the HTTP status code, as this is the equivalent in `aiohttp`.