### Explanation of Changes
To migrate the code from using the `flask` library to the `tornado` library, the following changes were made:
1. **Blueprint Replacement**: Flask's `Blueprint` is used for routing and serving static files. Tornado does not have a direct equivalent, so we replaced it with Tornado's `StaticFileHandler` for serving static files.
2. **Static File Handling**: Tornado requires explicit configuration for serving static files. We added a `tornado.web.Application` instance with a route for static files.
3. **Removed Flask-Specific Imports**: The `Blueprint` import from Flask was removed since it is no longer used.
4. **Tornado Application Setup**: A Tornado application and server were added to handle HTTP requests.

The rest of the code (e.g., the `BaseMap`, `Map`, and `AreaMap` classes) remains unchanged because it does not depend on Flask-specific functionality.

---

### Modified Code
```python
from jinja2.utils import htmlsafe_json_dumps
from markupsafe import Markup
import os
import re
import secrets
import tornado.ioloop
import tornado.web

# Define the static folder path
static_folder = os.path.abspath(__file__ + '/../../django/static')

# Tornado RequestHandler for serving static files
class StaticFileHandler(tornado.web.StaticFileHandler):
    def initialize(self, path):
        self.root = path

# Tornado Application
class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to the Tornado application!")

def make_app():
    return tornado.web.Application([
        (r"/", MainHandler),
        (r"/static/mapkick/(.*)", StaticFileHandler, {"path": static_folder}),
    ])

# BaseMap class and its subclasses remain unchanged
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

# Start the Tornado server
if __name__ == "__main__":
    app = make_app()
    app.listen(8888)
    print("Tornado server is running on http://localhost:8888")
    tornado.ioloop.IOLoop.current().start()
```

---

### Key Notes
1. The `make_app` function sets up the Tornado application with routes for the main handler and static files.
2. The `StaticFileHandler` is used to serve static files from the `static_folder` directory.
3. The `BaseMap`, `Map`, and `AreaMap` classes remain unchanged as they do not rely on Flask-specific features.