### Explanation of Changes
To migrate the code from Flask to CherryPy:
1. **Blueprint Replacement**: Flask's `Blueprint` is used for modularizing applications. CherryPy does not have a direct equivalent, so we replace it with a CherryPy application structure. The static file handling is implemented using CherryPy's `tools.staticdir` configuration.
2. **Static File Handling**: Flask's `static_folder` and `static_url_path` are replaced with CherryPy's static file serving mechanism.
3. **Application Structure**: CherryPy applications are typically defined as classes with methods corresponding to HTTP endpoints. Since the provided code does not define specific routes, we assume the static files are the primary concern and configure CherryPy to serve them.

### Modified Code
```python
import cherrypy
from jinja2.utils import htmlsafe_json_dumps
from markupsafe import Markup
import os
import re
import secrets

static_folder = os.path.abspath(__file__ + '/../../django/static')


class MapkickApp:
    @cherrypy.expose
    def index(self):
        return "Mapkick Application is running."

    @staticmethod
    def configure_static():
        # Configure static file serving
        cherrypy.config.update({
            '/static': {
                'tools.staticdir.on': True,
                'tools.staticdir.dir': static_folder
            }
        })


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


if __name__ == '__main__':
    # Configure and start the CherryPy application
    MapkickApp.configure_static()
    cherrypy.quickstart(MapkickApp(), '/')
```

### Key Changes
1. **Blueprint Replacement**: Removed `Blueprint` and replaced it with a CherryPy application class (`MapkickApp`).
2. **Static File Handling**: Configured CherryPy to serve static files from the `static_folder` directory under the `/static` URL path.
3. **Application Entry Point**: Added a `main` block to configure and start the CherryPy application using `cherrypy.quickstart`.

This code now uses CherryPy for serving the application and static files, replacing Flask's `Blueprint` and static file handling mechanisms.