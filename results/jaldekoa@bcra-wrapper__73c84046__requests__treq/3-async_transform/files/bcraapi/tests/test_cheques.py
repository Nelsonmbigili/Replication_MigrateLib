from bcraapi.cheques import entidades, denunciados
import pandas as pd
import pytest


@pytest.mark.asyncio
async def test_entidades():
    df = await entidades()
    assert isinstance(df, pd.DataFrame) and not df.empty


@pytest.mark.parametrize("codigo_entidad,numero_cheque,denunciado", [(11, 20377516, True), (11, 20377590, True)])
async def test_denunciados(codigo_entidad, numero_cheque, denunciado):
    df = await denunciados(codigo_entidad, numero_cheque)
    assert df['denunciado'].values == [denunciado]
