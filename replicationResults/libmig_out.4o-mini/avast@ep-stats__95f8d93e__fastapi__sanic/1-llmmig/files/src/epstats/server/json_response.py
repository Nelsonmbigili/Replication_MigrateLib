import json as json
import typing

from sanic.response import JSON


class DataScienceJsonResponse(JSON):
    media_type = "application/json"

    def render(self, content: typing.Any) -> bytes:
        # we need to use default json implementation and explicitly encode in utf-8 to
        # preserver `np.nan` and `np.inf` values.
        return json.dumps(content).encode("utf-8")
