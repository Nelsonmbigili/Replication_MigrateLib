from bcraapi import get_from_bcra
import pandas as pd


async def deudas(identificacion: int) -> pd.DataFrame:
    """
    Método para obtener la situación crediticia, el monto de deuda, los días de atraso y
    observaciones correspondientes al último período informada por las entidades al BCRA.

    Args:
        identificacion (int): Corresponde a CUIT/CUIL/CDI, la misma debe tener una longitud de 11 caracteres.

    Returns:
        pd.DataFrame: DataFrame con la situación crediticia, el monto de deuda, los días de atraso y observaciones correspondientes al último período informada por las entidades al BCRA para un CUIT/CUIL/CDI.
    """
    return await get_from_bcra(f"/centraldedeudores/v1.0/Deudas/{identificacion}")


async def deudas_historicas(identificacion: int) -> pd.DataFrame:
    """
    Método para obtener la situación crediticia relativa a los últimos 24 meses.
    Args:
        identificacion (int): Corresponde a CUIT/CUIL/CDI, la misma debe tener una longitud de 11 caracteres.
    Returns:
        pd.DataFrame: DataFrame con la situación crediticia relativa a los últimos 24 meses.
    """
    return await get_from_bcra(f"/centraldedeudores/v1.0/Deudas/Historicas/{identificacion}")


async def cheques_rechazados(identificacion: int) -> pd.DataFrame:
    """
    Método para obtener los cheques rechazados con sus correspondientes causales.

    Args:
        identificacion (int): Corresponde a CUIT/CUIL/CDI, la misma debe tener una longitud de 11 caracteres.
    Returns:
        pd.DataFrame: DataFrame con los cheques rechazados con sus correspondientes causales.
    """
    return await get_from_bcra(f"/centraldedeudores/v1.0/Deudas/ChequesRechazados/{identificacion}")
