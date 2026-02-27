from bcraapi.centraldeudores import deudas, deudas_historicas, cheques_rechazados
import pandas as pd
import pytest


@pytest.mark.parametrize("identificacion", [30500010912])
async def test_deudas(identificacion):
    df = await deudas(identificacion)
    assert (isinstance(df, pd.DataFrame) and not df.empty)


@pytest.mark.parametrize("identificacion", [30500010912])
async def test_deudas_historicas(identificacion):
    df = await deudas_historicas(identificacion)
    assert (isinstance(df, pd.DataFrame) and not df.empty)


@pytest.mark.parametrize("identificacion", [30717283186])
async def test_cheques_rechazados(identificacion):
    df = await cheques_rechazados(identificacion)
    assert (isinstance(df, pd.DataFrame) and not df.empty)
