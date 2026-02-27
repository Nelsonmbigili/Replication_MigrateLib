### Explanation of Changes:
To migrate the code from using the `requests` library to the `treq` library, the following changes were made:
1. **Asynchronous Nature of `treq`**: The `treq` library is asynchronous, so the `__connect_to_api` function was modified to be an `async` function. This requires the use of `await` for `treq` calls.
2. **Replacing `requests.get`**: The `requests.get` call was replaced with `treq.get`. The `verify` parameter is passed to `treq.get` to handle SSL certificate verification.
3. **Handling Responses**: `treq` provides response content as an asynchronous stream. The response content is read using `await response.json()` for JSON data.
4. **Error Handling**: The error handling logic was updated to work with the asynchronous response object provided by `treq`.
5. **Calling Asynchronous Functions**: Since `__connect_to_api` is now asynchronous, any function that calls it (e.g., `get_from_bcra`) must also be asynchronous.

### Modified Code:
```python
from typing import Union, Dict, List
import pandas as pd
import treq
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


async def __connect_to_api(url: str) -> dict:
    response = await treq.get(url, verify=__cert_path)

    if response.code == 200:
        return await response.json()['results']
    if response.code in [400, 404, 500]:
        error_data = await response.json()
        raise Exception(f"Error {error_data['status']}. {'.'.join(error_data['errorMessages'])}")


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


async def get_from_bcra(endpoint: str) -> pd.DataFrame:
    df = await __connect_to_api(url=f"{__base_url}{endpoint}")
    df = __json_to_df(df)
    df = __parse_cols(df)
    return df
```

### Key Notes:
1. **Asynchronous Functions**: Both `__connect_to_api` and `get_from_bcra` are now asynchronous (`async def`). This means they must be called using `await` in an asynchronous context.
2. **`treq.get`**: The `treq.get` function is used to make the HTTP GET request, with the `verify` parameter for SSL certificate verification.
3. **Response Handling**: The `response.json()` method is awaited to retrieve the JSON content from the response.
4. **Error Handling**: The error handling logic was updated to work with the asynchronous response object.

This migration ensures the code now uses `treq` while maintaining the original functionality and structure.