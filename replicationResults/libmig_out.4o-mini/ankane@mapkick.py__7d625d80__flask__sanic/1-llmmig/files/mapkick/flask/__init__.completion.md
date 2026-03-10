### Explanation of Changes

To migrate the provided code from using the Flask library to the Sanic library, the following changes were made:

1. **Blueprint Import**: The `Blueprint` class is imported from `sanic` instead of `flask`.
2. **Static Folder Handling**: The way static files are served is slightly different in Sanic. The `static_folder` and `static_url_path` parameters are still used, but they are part of the `Blueprint` initialization in Sanic.
3. **Markup Handling**: The `Markup` class from `markupsafe` remains unchanged, as it is compatible with both Flask and Sanic.
4. **Jinja2 Utilities**: The `htmlsafe_json_dumps` function is still used from `jinja2.utils`, as it is also compatible with Sanic.
5. **No Changes to Class and Function Names**: The class and function names remain unchanged to ensure compatibility with the larger application.

Here is the modified code:

```python
from sanic import Blueprint
from jinja2.utils import htmlsafe_json_dumps
from markupsafe import Markup
import os
import re
import secrets

static_folder = os.path.abspath(__file__ + '/../../django/static')
mapkick_blueprint = Blueprint('mapkick', __name__, static_folder=static_folder, static_url_path='/static/mapkick')


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