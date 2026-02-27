### Explanation of Changes
To migrate the code from the `requests` library to `aiohttp`, the following changes were made:
1. **Asynchronous Programming**: `aiohttp` is an asynchronous library, so all methods that use `aiohttp` for HTTP requests were converted to `async` functions.
2. **Session Management**: `aiohttp` requires an `aiohttp.ClientSession` for making requests. A session is created and used for all HTTP requests.
3. **Streamed Downloads**: The `aiohttp` equivalent of `requests.get(..., stream=True)` is `session.get(..., timeout=...)` with an `async for` loop to read chunks of data.
4. **JSON and Content Handling**: `aiohttp` provides `await response.json()` and `await response.read()` for JSON and raw content, respectively.
5. **Error Handling**: `aiohttp` raises exceptions for HTTP errors, so `response.raise_for_status()` is used to ensure proper error handling.
6. **File Writing**: File writing remains synchronous, as Python's standard file I/O is not asynchronous.

### Modified Code
Below is the modified code using `aiohttp`:

```python
import filestack.models
import aiohttp
import asyncio


class CommonMixin:
    """
    Contains all functions related to the manipulation of Filelink and Transformation objects
    """

    @property
    def url(self):
        """
        Returns object's URL

        >>> filelink.url
        'https://cdn.filestackcontent.com/FILE_HANDLE'
        >>> transformation.url
        'https://cdn.filestackcontent.com/resize=width:800/FILE_HANDLE'

        Returns:
            str: object's URL
        """
        return self._build_url()

    def signed_url(self, security=None):
        """
        Returns object's URL signed using security object

        >>> filelink.url
        'https://cdn.filestackcontent.com/security=p:<encoded_policy>,s:<signature>/FILE_HANDLE'
        >>> transformation.url
        'https://cdn.filestackcontent.com/resize=width:800/security=p:<encoded_policy>,s:<signature>/FILE_HANDLE'

        Args:
            security (:class:`filestack.Security`): Security object that will be used
                to sign url

        Returns:
            str: object's signed URL
        """
        sec = security or self.security
        if sec is None:
            raise ValueError('Security is required to sign url')
        return self._build_url(security=sec)

    async def store(self, filename=None, location=None, path=None, container=None,
                    region=None, access=None, base64decode=None, workflows=None):
        """
        Stores current object as a new :class:`filestack.Filelink`.

        Args:
            filename (str): name for the stored file
            location (str): your storage location, one of: :data:`"s3"` :data:`"azure"`
                :data:`"dropbox"` :data:`"rackspace"` :data:`"gcs"`
            container (str): the bucket or container (folder) in which to store the file
                (does not apply when storing to Dropbox)
            path (str): the path to store the file within the specified container
            region (str): your storage region (applies to S3 only)
            access (str): :data:`"public"` or :data:`"private"` (applies to S3 only)
            base64decode (bool): indicates if content should be decoded before it is stored
            workflows (list): IDs of `Filestack Workflows
                <https://www.filestack.com/products/workflows>`_ that should be triggered after upload

        Returns:
            :class:`filestack.Filelink`: new Filelink object
        """
        if path:
            path = '"{}"'.format(path)
        instance = self._add_transform_task('store', locals())
        async with aiohttp.ClientSession() as session:
            async with session.post(instance.url) as response:
                response.raise_for_status()
                data = await response.json()
        return filestack.models.Filelink(handle=data['handle'])

    async def download(self, path, security=None):
        """
        Downloads a file to the given local path and returns the size of the downloaded file if successful
        """
        sec = security or self.security
        total_bytes = 0

        async with aiohttp.ClientSession() as session:
            async with session.get(self._build_url(security=sec)) as response:
                response.raise_for_status()
                with open(path, 'wb') as f:
                    async for data_chunk in response.content.iter_chunked(5 * 1024 ** 2):
                        f.write(data_chunk)
                        total_bytes += len(data_chunk)

        return total_bytes

    async def get_content(self, security=None):
        """
        Returns the raw byte content of a given object

        Returns:
            `bytes`: file content
        """
        sec = security or self.security
        async with aiohttp.ClientSession() as session:
            async with session.get(self._build_url(security=sec)) as response:
                response.raise_for_status()
                return await response.read()

    async def tags(self, security=None):
        """
        Performs image tagging operation on current object (image)

        Args:
            security (:class:`filestack.Security`): Security object that will be used
                to perform image tagging

        Returns:
            `dict`: dictionary containing image tags
        """
        obj = self._add_transform_task('tags', params={'self': None})
        async with aiohttp.ClientSession() as session:
            async with session.get(obj.signed_url(security=security)) as response:
                response.raise_for_status()
                return await response.json()

    async def sfw(self, security=None):
        """
        Performs Safe for Work detection on current object (image).

        Args:
            security (:class:`filestack.Security`): Security object that will be used
                to perform image tagging

        Returns:
            `dict`: dictionary containing SFW result
        """
        obj = self._add_transform_task('sfw', params={'self': None})
        async with aiohttp.ClientSession() as session:
            async with session.get(obj.signed_url(security=security)) as response:
                response.raise_for_status()
                return await response.json()

    async def ocr(self, security=None):
        """
        Performs OCR on current object (image)

        Args:
            security (:class:`filestack.Security`): Security object that will be used
                to run OCR

        Returns:
            `dict`: dictionary containing OCR data
        """
        obj = self._add_transform_task('ocr', params={'self': None})
        async with aiohttp.ClientSession() as session:
            async with session.get(obj.signed_url(security=security)) as response:
                response.raise_for_status()
                return await response.json()
```

### Key Notes:
- All methods that perform HTTP requests (`store`, `download`, `get_content`, `tags`, `sfw`, `ocr`) are now `async` functions.
- The `aiohttp.ClientSession` is used for all HTTP requests, and proper cleanup is ensured using `async with`.
- The `await` keyword is used for asynchronous operations like `response.json()` and `response.read()`.
- File writing remains synchronous, as Python's standard file I/O does not support asynchronous operations.