### Explanation of Changes

To migrate the code from using the Flask framework to the Tornado framework, several key changes were made:

1. **Blueprints**: Tornado does not have a direct equivalent to Flask's Blueprint. Instead, we will define the error handlers directly in the application or a similar structure.
  
2. **Error Handling**: Tornado uses a different mechanism for error handling. Instead of using `app_errorhandler`, we will define custom error handlers and register them with the application.

3. **HTTP Exceptions**: Tornado has its own set of HTTP exceptions, and we will use `tornado.web.HTTPError` for handling HTTP errors.

4. **Current Application Context**: The `current_app` context from Flask is not available in Tornado. We will need to access the application configuration directly.

5. **Response Format**: The response format remains similar, but we will use Tornado's `tornado.web.RequestHandler` to send responses.

Here is the modified code:

```python
from tornado.web import RequestHandler, HTTPError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from api.app import apifairy

class ErrorHandler(RequestHandler):

    def http_error(self, error):
        self.set_status(error.code)
        self.write({
            'code': error.code,
            'message': error.name,
            'description': error.description,
        })

    def sqlalchemy_integrity_error(self, error):  # pragma: no cover
        self.set_status(400)
        self.write({
            'code': 400,
            'message': 'Database integrity error',
            'description': str(error.orig),
        })

    def sqlalchemy_error(self, error):  # pragma: no cover
        if self.application.settings['DEBUG'] is True:
            self.set_status(500)
            self.write({
                'code': 500,
                'message': 'Database error',
                'description': str(error),
            })
        else:
            self.set_status(500)
            self.write({
                'code': 500,
                'message': 'Internal Server Error',
                'description': 'An internal server error occurred.',
            })

@apifairy.error_handler
def validation_error(code, messages):  # pragma: no cover
    return {
        'code': code,
        'message': 'Validation Error',
        'description': ('The server found one or more errors in the '
                        'information that you sent.'),
        'errors': messages,
    }, code
```

### Notes:
- The `ErrorHandler` class extends `RequestHandler`, which allows us to handle requests and responses in Tornado.
- The error handling methods are now instance methods of the `ErrorHandler` class.
- The `self.application.settings['DEBUG']` is used to access the application configuration in Tornado.
- The `validation_error` function remains unchanged as it does not directly depend on Flask's context.