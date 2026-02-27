import json as json
import typing

from sanic.response import json as sanic_json


def DataScienceJsonResponse(content: typing.Any) -> bytes:
    # We need to use the default json implementation and explicitly encode in utf-8 to
    # preserve `np.nan` and `np.inf` values.
    return sanic_json(json.loads(json.dumps(content).encode("utf-8")))
