from typing import Union, Dict, List
import pandas as pd
import urllib3
import json
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

# Initialize a PoolManager for making HTTP requests
http = urllib3.PoolManager(cert_reqs="CERT_REQUIRED", ca_certs=__cert_path)


def __connect_to_api(url: str) -> dict:
    response = http.request("GET", url)

    if response.status == 200:
        # Decode the response data and parse it as JSON
        return json.loads(response.data.decode("utf-8"))['results']
    if response.status in [400, 404, 500]:
        error_data = json.loads(response.data.decode("utf-8"))
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


def get_from_bcra(endpoint: str) -> pd.DataFrame:
    df = __connect_to_api(url=f"{__base_url}{endpoint}")
    df = __json_to_df(df)
    df = __parse_cols(df)
    return df
