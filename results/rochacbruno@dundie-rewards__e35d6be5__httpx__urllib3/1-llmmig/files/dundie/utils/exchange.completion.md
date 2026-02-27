### Explanation of Changes
To migrate the code from using `httpx` to `urllib3`, the following changes were made:
1. **Import Changes**: Removed the `httpx` import and replaced it with `urllib3`.
2. **HTTP Request Handling**: Replaced `httpx.get()` with `urllib3.PoolManager().request()`. `urllib3` does not have a direct `get` method, so we use the `request` method with the HTTP method specified as `"GET"`.
3. **Response Handling**: `urllib3` returns a response object where the body is a byte string. To handle this:
   - Decoded the response body using `.data.decode("utf-8")`.
   - Parsed the JSON response using `json.loads()` (since `urllib3` does not have a built-in `.json()` method like `httpx`).
4. **Error Handling**: Checked the HTTP status code using `response.status` instead of `response.status_code`.

### Modified Code
```python
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
```

### Summary of Changes
- Replaced `httpx.get()` with `urllib3.PoolManager().request("GET", ...)`.
- Used `response.data.decode("utf-8")` and `json.loads()` to handle JSON parsing.
- Checked the HTTP status using `response.status` instead of `response.status_code`.
- Added `import json` for JSON parsing since `urllib3` does not provide a `.json()` method.