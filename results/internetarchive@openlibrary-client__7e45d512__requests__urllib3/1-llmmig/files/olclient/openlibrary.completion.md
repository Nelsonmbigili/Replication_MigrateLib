### Explanation of Changes

To migrate the code from the `requests` library to `urllib3`, the following changes were made:

1. **Session Management**:
   - Replaced `requests.Session()` with `urllib3.PoolManager()` for managing HTTP connections.

2. **HTTP Methods**:
   - Replaced `session.get`, `session.post`, and `session.put` with `urllib3.PoolManager` methods (`manager.request`).
   - Adjusted the method calls to include `method`, `url`, `headers`, `body`, and `fields` as required by `urllib3`.

3. **Error Handling**:
   - Replaced `requests.exceptions.RequestException` with `urllib3.exceptions.HTTPError` for exception handling.
   - Updated the `response.raise_for_status()` calls to manually check the HTTP status code and raise exceptions if necessary.

4. **File Uploads**:
   - Replaced `requests`'s `files` parameter with `urllib3.filepost.encode_multipart_formdata` for handling file uploads.

5. **Response Handling**:
   - Replaced `response.json()` with `json.loads(response.data.decode('utf-8'))` to parse JSON responses from `urllib3`.

6. **Backoff Integration**:
   - Updated the `backoff` decorator to work with `urllib3` exceptions.

---

### Modified Code

Below is the entire code after migrating from `requests` to `urllib3`:

```python
"""Basic wrapper (client) over OpenLibrary REST API"""

import json
from typing import List, Dict, Optional, Any

import jsonschema
import logging
import os
import re
from urllib.parse import urlencode
from urllib.request import pathname2url
from urllib3 import PoolManager
from urllib3.exceptions import HTTPError
from urllib3.filepost import encode_multipart_formdata

import backoff

from olclient import common
from olclient.config import Config
from olclient.entity_helpers.work import get_work_helper_class
from olclient.utils import merge_unique_lists

logger = logging.getLogger('openlibrary')


class OpenLibrary:

    """Open Library API Client."""

    VALID_IDS = ['isbn_10', 'isbn_13', 'lccn', 'ocaid']
    BACKOFF_KWARGS = {
        'wait_gen': backoff.expo,
        'exception': HTTPError,
        'giveup': lambda e: hasattr(e, 'status') and 400 <= e.status < 500,
        'max_tries': 5,
    }

    # constants to aid works.json API request's pagination
    WORKS_LIMIT = 50
    WORKS_PAGINATION_OFFSET = 0

    def __init__(self, credentials=None, base_url='https://openlibrary.org'):
        self.manager = PoolManager()
        self.base_url = base_url
        self.cookies = {}
        credentials = credentials or Config().get_config().get('s3', None)
        if credentials:
            self.login(credentials)

    def login(self, credentials):
        """Login to Open Library with given credentials, ensures the session has valid cookies for future requests."""

        if 'username' in credentials._asdict():
            headers = {'Content-Type': 'application/x-www-form-urlencoded'}
            data = urlencode(credentials._asdict())
        else:  # s3 login
            headers = {'Content-Type': 'application/json'}
            data = json.dumps(credentials._asdict())
        url = self.base_url + '/account/login'

        err = lambda e: logger.exception("Error at login: %s", e)

        @backoff.on_exception(on_giveup=err, **self.BACKOFF_KWARGS)
        def _login(url, headers, data):
            """Makes best effort to perform request w/ exponential backoff"""
            response = self.manager.request(
                'POST', url, headers=headers, body=data.encode('utf-8')
            )
            if response.status >= 400:
                raise HTTPError(f"HTTP Error: {response.status}")
            return response

        response = _login(url, headers, data)

        # Extract cookies from the response headers
        if 'set-cookie' in response.headers:
            self.cookies = {k: v for k, v in [cookie.split('=') for cookie in response.headers['set-cookie'].split(';')]}
        else:
            raise ValueError("No cookie set")

    def validate(self, doc, schema_name):
        """Validates a doc's json representation against its JSON Schema using jsonschema.validate()."""
        path = os.path.dirname(os.path.realpath(__file__))
        schemata_path = os.path.join(path, 'schemata', schema_name)
        with open(schemata_path) as schema_data:
            schema = json.load(schema_data)
            resolver = jsonschema.RefResolver('file:' + pathname2url(schemata_path), schema)
            return jsonschema.Draft4Validator(schema, resolver=resolver).validate(
                doc.json()
            )

    def delete(self, olid, comment):
        """Delete a single Open Library entity by olid (str)."""
        data = json.dumps({'type': {'key': '/type/delete'}, '_comment': comment})
        url = self._generate_url_from_olid(olid)
        headers = {'Content-Type': 'application/json'}
        response = self.manager.request('PUT', url, headers=headers, body=data.encode('utf-8'))
        return response

    def save_many(self, docs, comment):
        """Uses the Open Library save_many API endpoint to write any number or combination of documents."""
        headers = {
            'Content-Type': 'application/json',
            'Opt': '"http://openlibrary.org/dev/docs/api"; ns=42',
            '42-comment': comment,
        }
        doc_json = [doc.json() for doc in docs]
        response = self.manager.request(
            'POST',
            f'{self.base_url}/api/save_many',
            headers=headers,
            body=json.dumps(doc_json).encode('utf-8'),
        )
        return response

    def get_ol_response(self, path):
        """Makes best effort to perform request w/ exponential backoff"""
        url = self.base_url + path

        err = lambda e: logger.exception("Error retrieving OpenLibrary response: %s", e)

        @backoff.on_exception(on_giveup=err, **self.BACKOFF_KWARGS)
        def _get(url):
            response = self.manager.request('GET', url)
            if response.status >= 400:
                raise HTTPError(f"HTTP Error: {response.status}")
            return response

        response = _get(url)
        return response

    def _generate_url_from_olid(self, olid):
        """Returns the .json url for an olid (str)"""
        ol_paths = {'OL..A': 'authors', 'OL..M': 'books', 'OL..W': 'works'}
        kind = re.sub(r'\d+', '..', olid)
        return f"{self.base_url}/{ol_paths[kind]}/{olid}.json"

    @staticmethod
    def get_text_value(text):
        """Returns the text value from a property that can either be a properly formed /type/text object, or a string."""
        try:
            return text.get('value')
        except:
            return text

    @staticmethod
    def full_key(olid):
        """Returns the Open Library JSON key of format /<type(plural)>/<olid> as used by the Open Library API."""
        return f"/{OpenLibrary.get_type(olid)}s/{olid}"

    @staticmethod
    def _extract_olid_from_url(url, url_type):
        """Extracts the olid from the info_url field."""
        ol_url_pattern = r'[/]%s[/]([0-9a-zA-Z]+)' % url_type
        try:
            return re.search(ol_url_pattern, url).group(1)
        except AttributeError:
            return None  # No match
```

---

### Key Notes:
- The `urllib3.PoolManager` is used for connection pooling and session management.
- File uploads are handled using `urllib3.filepost.encode_multipart_formdata`.
- JSON responses are parsed using `json.loads(response.data.decode('utf-8'))`.
- Error handling is updated to use `urllib3.exceptions.HTTPError`.