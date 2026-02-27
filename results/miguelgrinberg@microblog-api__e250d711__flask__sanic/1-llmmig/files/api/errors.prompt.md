The following Python code currently uses the library "flask" version 3.0.3.
Migrate this code to use the library "sanic" version 25.3.0 instead.

**Instructions:**
1. **Explain the Changes**: Begin the output with a brief explanation of the specific changes you made to migrate from "flask" to "sanic".
2. **Provide the Modified Code**: After the explanation, present the modified code. Provide the entire code after migration even if only a part of it is changed.

**Important Guidelines**:
- Only make changes directly related to migrating between "flask" and "sanic".
- Do not refactor, reformat, optimize, or alter the original coding style.
- The code given to you is part of a larger application. Do not change the names of classes, functions, or variables, because it can break the application.

Original code:
```python
from flask import Blueprint, current_app
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from werkzeug.exceptions import HTTPException, InternalServerError

from api.app import apifairy

errors = Blueprint('errors', __name__)


@errors.app_errorhandler(HTTPException)
def http_error(error):
    return {
        'code': error.code,
        'message': error.name,
        'description': error.description,
    }, error.code


@errors.app_errorhandler(IntegrityError)
def sqlalchemy_integrity_error(error):  # pragma: no cover
    return {
        'code': 400,
        'message': 'Database integrity error',
        'description': str(error.orig),
    }, 400


@errors.app_errorhandler(SQLAlchemyError)
def sqlalchemy_error(error):  # pragma: no cover
    if current_app.config['DEBUG'] is True:
        return {
            'code': InternalServerError.code,
            'message': 'Database error',
            'description': str(error),
        }, 500
    else:
        return {
            'code': InternalServerError.code,
            'message': InternalServerError().name,
            'description': InternalServerError.description,
        }, 500


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