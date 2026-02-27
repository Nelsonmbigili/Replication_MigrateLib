### Explanation of Changes:
To migrate the code from using the `requests` library to `pycurl`, the following changes were made:
1. **Replaced `requests.get` with `pycurl`**:
   - `pycurl` requires setting up a `pycurl.Curl` object and configuring it with the necessary options (e.g., URL, SSL certificate, etc.).
   - The response data is captured using a `BytesIO` object since `pycurl` writes the response directly to a file-like object.
2. **Error Handling**:
   - `pycurl` does not provide built-in HTTP status code handling like `requests`. Instead, the HTTP status code is retrieved using the `getinfo` method of the `Curl` object.
   - Custom error handling was added to check the HTTP status code and raise exceptions accordingly.
3. **Certificate Verification**:
   - The `pycurl` equivalent of `verify` in `requests` is setting the `CAINFO` option to the certificate path.

Below is the modified code:

---

### Modified Code:
```python
from typing import Union, Dict, List
import pandas as pd
import pycurl
import os
from io import BytesIO
import json

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
    # Initialize a BytesIO object to capture the response
    response_buffer = BytesIO()
    curl = pycurl.Curl()

    try:
        # Set up the pycurl options
        curl.setopt(pycurl.URL, url)
        curl.setopt(pycurl.WRITEFUNCTION, response_buffer.write)
        curl.setopt(pycurl.CAINFO, __cert_path)  # Set the certificate path for SSL verification

        # Perform the request
        curl.perform()

        # Get the HTTP status code
        status_code = curl.getinfo(pycurl.RESPONSE_CODE)

        # Check the status code and handle errors
        if status_code == 200:
            # Decode the response and parse JSON
            response_data = response_buffer.getvalue().decode('utf-8')
            return json.loads(response_data)['results']
        elif status_code in [400, 404, 500]:
            # Decode the response and parse JSON for error messages
            response_data = response_buffer.getvalue().decode('utf-8')
            error_data = json.loads(response_data)
            raise Exception(f"Error {error_data['status']}. {'.'.join(error_data['errorMessages'])}")
        else:
            raise Exception(f"Unexpected HTTP status code: {status_code}")
    finally:
        # Clean up the curl object and close the buffer
        curl.close()
        response_buffer.close()


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

---

### Key Points:
1. The `requests.get` call was replaced with a `pycurl.Curl` object configured to perform an HTTPS GET request.
2. The response is captured using a `BytesIO` object, and the data is decoded and parsed as JSON.
3. Error handling was implemented to check the HTTP status code and raise exceptions for specific error codes (400, 404, 500).
4. The certificate verification is handled using the `CAINFO` option in `pycurl`.

This ensures the functionality remains consistent while using the `pycurl` library.