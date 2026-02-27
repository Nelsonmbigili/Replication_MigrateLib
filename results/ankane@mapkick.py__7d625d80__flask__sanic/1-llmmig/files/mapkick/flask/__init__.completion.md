### Explanation of Changes
To migrate the code from Flask to Sanic, the following changes were made:
1. **Blueprint Replacement**: Flask's `Blueprint` was replaced with Sanic's `Blueprint`. The import statement and the initialization of the `mapkick_blueprint` were updated accordingly.
2. **Static File Handling**: Sanic handles static files differently. Instead of specifying `static_folder` and `static_url_path` in the `Blueprint`, Sanic requires static files to be registered explicitly using the `Blueprint.static()` method.
3. **Markup and HTML Escaping**: Sanic does not have a direct equivalent of Flask's `Markup` class. However, since the `Markup` class in Flask is primarily used to mark strings as safe for HTML rendering, the same functionality can be achieved in Sanic by directly using the string (assuming the string is already safe).
4. **No Changes to Core Logic**: The rest of the code (e.g., `BaseMap`, `Map`, and `AreaMap` classes) remains unchanged, as it does not depend on Flask-specific features.

### Modified Code
```python
from sanic import Blueprint
from jinja2.utils import htmlsafe_json_dumps
import os
import re
import secrets

static_folder = os.path.abspath(__file__ + '/../../django/static')
mapkick_blueprint = Blueprint('mapkick', url_prefix='/static/mapkick')
mapkick_blueprint.static('/', static_folder)


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
        html = """<div id="%(element_id)s" style="height: %(height)s; width: %(width)s;"><div style="height: %(height)s; text-align: center; color: #999; line-height: %(height)s; font-size: 14px; font-family: 'Lucida Grande', 'Lucida Sans Unicode', Verdana, Arial, Helvetica, sans-serif;">%(loading)s</div></div>""" % html_vars

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
        js = """<script>
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
</script>""" % htmlsafe_json_dumps(js_vars)

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
- The `mapkick_blueprint` now uses Sanic's `Blueprint` and explicitly registers the static folder using `Blueprint.static()`.
- The `Markup` class from Flask was removed, and the HTML strings are directly used, assuming they are safe.
- No other changes were made to the logic or structure of the code to ensure compatibility with the rest of the application.