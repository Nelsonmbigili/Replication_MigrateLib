The following Python code currently uses the library "requests" version 2.31.0.
Migrate this code to use the library "aiohttp" version 3.11.16 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "requests" to "aiohttp".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "requests" and "aiohttp".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from typing import Union, Dict, List
import pandas as pd
import requests
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


def __connect_to_api(url: str) -> dict:
    res = requests.get(url, verify=__cert_path)

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