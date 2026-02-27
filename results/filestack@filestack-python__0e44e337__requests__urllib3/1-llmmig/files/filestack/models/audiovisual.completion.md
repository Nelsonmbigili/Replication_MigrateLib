### Explanation of Changes
To migrate the code from using the `requests` library to `urllib3`, the following changes were made:
1. **Importing `urllib3`**: The `requests` library was removed, and `urllib3` was imported instead.
2. **Creating an HTTP Connection Pool**: `urllib3` requires an explicit HTTP connection pool manager (`urllib3.PoolManager`) to handle HTTP requests.
3. **Replacing `requests.get`**: The `requests.get` calls were replaced with `urllib3.PoolManager().request` calls. The `request` method requires specifying the HTTP method (e.g., `'GET'`) and returns a response object.
4. **Parsing JSON Responses**: Unlike `requests`, `urllib3` does not have a built-in `.json()` method for parsing JSON responses. Instead, the `json` module from Python's standard library was used to parse the response data.

### Modified Code
```python
import filestack.models
import urllib3
import json


class AudioVisual:

    def __init__(self, url, uuid, timestamp, apikey=None, security=None):
        """
        AudioVisual instances provide a bridge between transform and filelinks, and allow
        you to check the status of a conversion and convert to a Filelink once completed

        ```python
        from filestack import Client

        client = Client("<API_KEY>")
        filelink = client.upload(filepath='path/to/file/doom.mp4')
        av_convert= filelink.av_convert(width=100, height=100)
        while av_convert.status != 'completed':
            print(av_convert.status)

        filelink = av_convert.to_filelink()
        print(filelink.url)
        ```
        """
        self.url = url
        self.apikey = apikey
        self.security = security
        self.uuid = uuid
        self.timestamp = timestamp
        self.http = urllib3.PoolManager()  # Create a connection pool manager

    def to_filelink(self):
        """
        Checks is the status of the conversion is complete and, if so, converts to a Filelink

        *returns* [Filestack.Filelink]

        ```python
        filelink = av_convert.to_filelink()
        ```
        """
        if self.status != 'completed':
            raise Exception('Audio/video conversion not complete!')

        response = self.http.request('GET', self.url)  # Perform a GET request
        response_data = json.loads(response.data.decode('utf-8'))  # Parse JSON response
        handle = response_data['data']['url'].split('/')[-1]
        return filestack.models.Filelink(handle, apikey=self.apikey, security=self.security)

    @property
    def status(self):
        """
        Returns the status of the AV conversion (makes a GET request)

        *returns* [String]

        ```python
        av_convert= filelink.av_convert(width=100, height=100)
        while av_convert.status != 'completed':
            print(av_convert.status)
        ```
        """
        response = self.http.request('GET', self.url)  # Perform a GET request
        response_data = json.loads(response.data.decode('utf-8'))  # Parse JSON response
        return response_data['status']
```

### Key Points
- The `urllib3.PoolManager` instance (`self.http`) is created in the `__init__` method to manage HTTP connections.
- The `urllib3.PoolManager().request` method is used to make HTTP requests, replacing `requests.get`.
- The `json.loads` function is used to parse the JSON response from `urllib3`, as `urllib3` does not provide a `.json()` method.
- The rest of the code remains unchanged to ensure compatibility with the larger application.