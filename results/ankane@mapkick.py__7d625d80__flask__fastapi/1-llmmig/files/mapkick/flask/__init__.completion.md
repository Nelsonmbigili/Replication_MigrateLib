### Explanation of Changes
To migrate the given code from Flask to FastAPI, the following changes were made:
1. **Blueprint Replacement**: Flask's `Blueprint` is replaced with FastAPI's `APIRouter`. The `Blueprint` was used to define a group of routes and static files. In FastAPI, `APIRouter` serves a similar purpose.
2. **Static Files Handling**: Flask's `static_folder` and `static_url_path` are replaced with FastAPI's `StaticFiles` from `fastapi.staticfiles`. The static files are mounted to serve them at a specific URL path.
3. **No Changes to Core Logic**: The core logic of the `BaseMap`, `Map`, and `AreaMap` classes remains unchanged, as it is independent of the web framework.

### Modified Code
Here is the complete code after migrating to FastAPI:

```python
from fastapi import APIRouter
from fastapi.staticfiles import StaticFiles
from jinja2.utils import htmlsafe_json_dumps
from markupsafe import Markup
import os
import re
import secrets

# Define the static folder path
static_folder = os.path.abspath(__file__ + '/../../django/static')

# Create an APIRouter instance
mapkick_router = APIRouter()

# Mount the static files
mapkick_router.mount("/static/mapkick", StaticFiles(directory=static_folder), name="static-mapkick")


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

### Key Notes
- The `mapkick_router` is an `APIRouter` instance, and the static files are mounted using `StaticFiles`. This is the FastAPI equivalent of Flask's `Blueprint` with `static_folder` and `static_url_path`.
- The rest of the code, including the `BaseMap`, `Map`, and `AreaMap` classes, remains unchanged because it does not depend on the web framework.
- The `mapkick_router` can now be included in a FastAPI application using `app.include_router(mapkick_router)`.