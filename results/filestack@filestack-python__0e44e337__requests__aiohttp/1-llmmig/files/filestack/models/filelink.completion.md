### Explanation of Changes
To migrate the code from `requests` to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: `aiohttp` is an asynchronous library, so the methods that make HTTP requests (`metadata`, `delete`, and `overwrite`) were converted to asynchronous methods using `async def`.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` for making requests. A session is created and used for all HTTP calls.
3. **Request Methods**: The `requests.get`, `requests.delete`, and `requests.post` calls were replaced with their `aiohttp` equivalents (`session.get`, `session.delete`, and `session.post`).
4. **Response Handling**: `aiohttp` responses are asynchronous, so `.json()` and `.text()` methods are awaited.
5. **File Uploads**: File uploads in `aiohttp` require the use of `aiohttp.FormData` for handling multipart form data.
6. **Error Handling**: Exceptions specific to `aiohttp` (e.g., `aiohttp.ClientError`) were not explicitly handled, as the original code did not include error handling for `requests`.

### Modified Code
```python
from filestack import config
from filestack.utils import requests
from filestack.mixins import CommonMixin
from filestack.mixins import ImageTransformationMixin
import aiohttp


class Filelink(ImageTransformationMixin, CommonMixin):
    """
    Filelink object represents a file that whas uploaded to Filestack.
    A filelink object can be created by uploading a file using Client instance,
    or by initializing Filelink class with a handle (unique id) of already uploaded file.

    >>> from filestack import Filelink
    >>> flink = Filelink('sm9IEXAMPLEQuzfJykmA')
    >>> flink.url
    'https://cdn.filestackcontent.com/sm9IEXAMPLEQuzfJykmA'
    """
    def __init__(self, handle, apikey=None, security=None, upload_response=None):
        """
        Args:
            handle (str): The path of the file to wrap
            apikey (str): Filestack API key that may be required for some API calls
            security (:class:`filestack.Security`): Security object that will be used by default
               for all API calls
        """
        self.apikey = apikey
        self.handle = handle
        self.security = security
        self.upload_response = upload_response

    def __repr__(self):
        return '<Filelink {}>'.format(self.handle)

    def _build_url(self, security=None):
        url_elements = [config.CDN_URL, self.handle]
        if security is not None:
            url_elements.insert(-1, security.as_url_string())
        return '/'.join(url_elements)

    async def metadata(self, attributes_list=None, security=None):
        """
        Retrieves filelink's metadata.

        Args:
            attributes_list (list): list of attributes that you wish to receive. When not provided,
                default set of parameters will be returned (may differ depending on your storage settings)
            security (:class:`filestack.Security`): Security object that will be used
                to retrieve metadata

        >>> filelink.metadata(['size', 'filename'])
        {'filename': 'envelope.jpg', 'size': 171832}

        Returns:
            `dict`: A buffered writable file descriptor
        """
        attributes_list = attributes_list or []
        params = {}
        for item in attributes_list:
            params[item] = 'true'
        sec = security or self.security
        if sec is not None:
            params.update({'policy': sec.policy_b64, 'signature': sec.signature})

        async with aiohttp.ClientSession() as session:
            async with session.get(self.url + '/metadata', params=params) as response:
                return await response.json()

    async def delete(self, apikey=None, security=None):
        """
        Deletes filelink.

        Args:
            apikey (str): Filestack API key that will be used for this API call
            security (:class:`filestack.Security`): Security object that will be used
                to delete filelink

        Returns:
            None
        """
        sec = security or self.security
        apikey = apikey or self.apikey

        if sec is None:
            raise Exception('Security is required to delete filelink')

        if apikey is None:
            raise Exception('Apikey is required to delete filelink')

        url = '{}/file/{}'.format(config.API_URL, self.handle)
        delete_params = {
            'key': apikey,
            'policy': sec.policy_b64,
            'signature': sec.signature
        }

        async with aiohttp.ClientSession() as session:
            async with session.delete(url, params=delete_params) as response:
                await response.text()

    async def overwrite(self, *, filepath=None, url=None, file_obj=None, base64decode=False, security=None):
        """
        Overwrites filelink with new content

        Args:
            filepach (str): path to file
            url (str): file URL
            file_obj (io.BytesIO or similar): file-like object
            base64decode (bool): indicates if content should be decoded before it is stored
            security (:class:`filestack.Security`): Security object that will be used
                to overwrite filelink

        Note:
            This method accepts keyword arguments only.
            Out of filepath, url and file_obj only one should be provided.
        """
        sec = security or self.security
        if sec is None:
            raise Exception('Security is required to overwrite filelink')
        req_params = {
            'policy': sec.policy_b64,
            'signature': sec.signature,
            'base64decode': str(base64decode).lower()
        }

        request_url = '{}/file/{}'.format(config.API_URL, self.handle)
        async with aiohttp.ClientSession() as session:
            if url:
                async with session.post(request_url, params=req_params, data={'url': url}) as response:
                    await response.text()
            elif filepath:
                with open(filepath, 'rb') as f:
                    form = aiohttp.FormData()
                    form.add_field('fileUpload', f, filename='filename', content_type='application/octet-stream')
                    async with session.post(request_url, params=req_params, data=form) as response:
                        await response.text()
            elif file_obj:
                form = aiohttp.FormData()
                form.add_field('fileUpload', file_obj, filename='filename', content_type='application/octet-stream')
                async with session.post(request_url, params=req_params, data=form) as response:
                    await response.text()
            else:
                raise Exception('filepath, file_obj or url argument must be provided')

        return self
```

### Key Notes
- The `metadata`, `delete`, and `overwrite` methods are now asynchronous and must be called using `await`.
- The `aiohttp.ClientSession` is used for all HTTP requests, and responses are awaited.
- File uploads use `aiohttp.FormData` to handle multipart form data.