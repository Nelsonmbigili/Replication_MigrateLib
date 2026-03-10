### Explanation of Changes

To migrate the provided code from using the Flask framework to the CherryPy framework, the following changes were made:

1. **Blueprint Replacement**: The `Blueprint` from Flask is not directly available in CherryPy. Instead, we will define a CherryPy application and use CherryPy's routing capabilities to handle requests.
  
2. **Static File Handling**: In Flask, static files are served using the `static_folder` and `static_url_path` parameters in the `Blueprint`. In CherryPy, we will set up a static file handler using CherryPy's built-in capabilities.

3. **Request Handling**: The way requests are handled in CherryPy is different from Flask. We will define a CherryPy application class that will handle the requests.

4. **HTML Rendering**: The rendering of HTML remains largely the same, but we will ensure that the response is returned correctly in the context of a CherryPy application.

Here is the modified code:

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
    @cherrypy.tools.staticfile.handler(static_folder=static_folder)
    def static(self, *args, **kwargs):
        return static_folder

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
    cherrypy.quickstart(MapkickApp(), '/', {'/': {'tools.sessions.on': True}})
```

### Summary of Changes
- Introduced a `MapkickApp` class to handle requests and serve static files.
- Replaced the Flask `Blueprint` with CherryPy's routing and static file handling.
- Used `cherrypy.expose` to define the endpoint for serving static files. 
- The main application is started using `cherrypy.quickstart()`.