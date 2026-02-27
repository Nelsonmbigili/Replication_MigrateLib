from bcraapi.estadisticas import monetarias
from datetime import datetime
import pandas as pd
import pytest

variable_ids = monetarias()["idVariable"].tolist()


@pytest.mark.asyncio
async def test_monetarias():
    df = await monetarias()
    assert isinstance(df, pd.DataFrame) and not df.empty


@pytest.mark.parametrize("id_variable", variable_ids)
async def test_monetarias_idVariable(id_variable):
    df = await monetarias(id_variable, hasta=f"{datetime.today():%Y-%m-%d}")
    assert (isinstance(df, pd.DataFrame) and not df.empty)
