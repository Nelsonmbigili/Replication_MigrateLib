### Explanation of Changes:
To migrate the code from using the `requests` library to `requests_futures`, the following changes were made:
1. **Import Change**: Replaced the `requests` import with `requests_futures.sessions` to use the `FuturesSession` class.
2. **Session Initialization**: Created a `FuturesSession` object to handle asynchronous requests.
3. **Request Handling**: Replaced the `requests.get` call with `session.get` (from the `FuturesSession` object). Since `requests_futures` returns a `Future` object, the `.result()` method is used to retrieve the response synchronously.
4. **No Other Changes**: The rest of the code remains unchanged, as the migration only affects how HTTP requests are made.

### Modified Code:
```python
from typing import Union, Dict, List
import pandas as pd
from requests_futures.sessions import FuturesSession
import os

__all__ = ["get_from_bcra", "estadisticas", "cheques", "estadisticascambiarias", "centraldeudores"]

__base_url = "https://api.bcra.gob.ar"
__cert_path = os.path.join(os.path.dirname(__file__), "cert/bcra.gob.ar.crt")

__cols_to_parse = {
    "idVariable": pd.to_numeric,
    "cdSerie": pd.to_numeric,
    "fecha": pd.to_datetime,
    "valor": pd.to_numeric,
    "fechaProcesamiento": pd.to_datetime,
    "codigoEntidad": pd.to_numeric,
    "numeroCuenta": pd.to_numeric,
}

# Initialize a FuturesSession for asynchronous requests
session = FuturesSession()

def __connect_to_api(url: str) -> dict:
    # Use session.get instead of requests.get
    future = session.get(url, verify=__cert_path)
    res = future.result()  # Wait for the response and retrieve it

    if res.status_code == 200:
        return res.json()['results']
    if res.status_code in [400, 404, 500]:
        raise Exception(f"Error {res.json()['status']}. {'.'.join(res.json()['errorMessages'])}")


def __flatten_dict(d: dict, parent_key: str = '', sep: str = '_') -> dict:
    items = []
    for k, v in d.items():
        if isinstance(v, dict):
            items.extend(__flatten_dict(v, parent_key, sep=sep).items())
        elif isinstance(v, list):
            for item in v:
                items.extend(__flatten_dict(item, parent_key, sep=sep).items())
        else:
            items.append((k, v))
    return dict(items)


def __json_to_df(json: Union[Dict, List]) -> pd.DataFrame:
    if isinstance(json, dict):
        json = __flatten_dict(json)
        return pd.DataFrame([json])
    elif isinstance(json, list):
        flattened_list = [__flatten_dict(item) for item in json]
        return pd.DataFrame(flattened_list)


def __parse_cols(df: pd.DataFrame) -> pd.DataFrame:
    for col in df.columns:
        df[col] = __cols_to_parse[col](df[col]) if col in __cols_to_parse else df[col]
    return df


def get_from_bcra(endpoint: str) -> pd.DataFrame:
    df = __connect_to_api(url=f"{__base_url}{endpoint}")
    df = __json_to_df(df)
    df = __parse_cols(df)
    return df
```

### Key Points:
- The `FuturesSession` object is used to make asynchronous HTTP requests.
- The `.result()` method ensures that the response is retrieved synchronously, maintaining the original behavior of the code.
- No other parts of the code were altered, ensuring compatibility with the rest of the application.