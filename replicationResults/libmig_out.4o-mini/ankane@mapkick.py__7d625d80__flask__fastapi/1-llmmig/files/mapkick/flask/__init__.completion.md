### Explanation of Changes

To migrate the provided code from Flask to FastAPI, the following changes were made:

1. **Blueprint Replacement**: FastAPI does not use Blueprints like Flask. Instead, we define routes directly in the FastAPI application instance.
2. **Static Files Handling**: FastAPI has built-in support for serving static files, which is configured differently than in Flask.
3. **Markup and JSON Handling**: FastAPI uses Pydantic for data validation and serialization, but since the original code does not require changes in data handling, we kept the existing logic for HTML and JavaScript generation.
4. **Initialization of FastAPI**: We created an instance of FastAPI to replace the Flask app.

The overall structure of the classes and methods remains unchanged, as per the instructions.

### Modified Code

```python
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from jinja2.utils import htmlsafe_json_dumps
from markupsafe import Markup
import os
import re
import secrets

app = FastAPI()
static_folder = os.path.abspath(__file__ + '/../../django/static')
app.mount("/static/mapkick", StaticFiles(directory=static_folder), name="static")

class BaseMap:
    def __init__(self, type, data, **options):
        # important! check escaping before making configurable
        element_id = 'map-' + secrets.token_hex(16)

        height = str(options.pop('height', '500px'))
        width = str(options.pop('width', '100%'))

        for (k, v) in [('height', height), ('width', width)]:
            # limit to alphanumeric and % for simplicity
            # this prevents things like calc() but safety is the priority
            # dot does not need escaped in square brackets
            if not re.match('^[a-zA-Z0-9%.]*$', v):
                raise ValueError('Invalid ' + k)

        html_vars = {
            'element_id': element_id,
            'height': height,
            'width': width,
            'loading': options.get('loading', 'Loading...')
        }
        html = Markup("""<div id="%(element_id)s" style="height: %(height)s; width: %(width)s;"><div style="height: %(height)s; text-align: center; color: #999; line-height: %(height)s; font-size: 14px; font-family: 'Lucida Grande', 'Lucida Sans Unicode', Verdana, Arial, Helvetica, sans-serif;">%(loading)s</div></div>""") % html_vars

        access_token = options.pop('access_token', options.pop('accessToken', os.environ.get('MAPBOX_ACCESS_TOKEN')))
        if access_token is not None:
            if access_token.startswith('sk.'):
                raise ValueError('Expected public access token')
            elif not access_token.startswith('pk.'):
                raise ValueError('Invalid access token')
            options['accessToken'] = access_token

        js_vars = {
            'type': type,
            'id': element_id,
            'data': data,
            'options': options
        }
        js = Markup("""<script>
  (function() {
    var createMap = function() {
      var o = %s;
      new Mapkick[o.type](o.id, o.data, o.options);
    };
    if ("Mapkick" in window) {
      createMap();
    } else {
      window.addEventListener("mapkick:load", createMap, true);
    }
  })();
</script>""") % htmlsafe_json_dumps(js_vars)

        self.__str = html + js

    def __str__(self):
        return self.__str

    def __html__(self):
        return self.__str


class Map(BaseMap):
    def __init__(self, data, **options):
        super().__init__('Map', data, **options)


class AreaMap(BaseMap):
    def __init__(self, data, **options):
        super().__init__('AreaMap', data, **options)
``` 

This code now uses FastAPI for handling requests and serving static files, while maintaining the original logic and structure of the classes.