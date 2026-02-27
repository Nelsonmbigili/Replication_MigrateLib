### Explanation of Changes
The migration from the `requests` library to the `treq` library involves the following changes:
1. **Asynchronous Nature of `treq`**: `treq` is built on top of `Twisted` and is asynchronous. Therefore, all functions that use `treq` must be converted to asynchronous functions using `async def`.
2. **Replacing `requests` Methods**: The `requests` methods (`get`, `post`, etc.) are replaced with their `treq` equivalents (`treq.get`, `treq.post`, etc.).
3. **Handling Responses**: `treq` methods return a `Deferred` object, so we use `await` to resolve it and extract the response content using methods like `response.text()`, `response.json()`, or `response.content()`.
4. **Streaming**: For streaming downloads, `treq` provides an `iter_content`-like functionality using `response.iter_chunks()`.

Below is the modified code with these changes applied.

---

### Modified Code
```python
import filestack.models
import treq


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
        response = await treq.post(instance.url)
        response_json = await response.json()
        return filestack.models.Filelink(handle=response_json['handle'])

    async def download(self, path, security=None):
        """
        Downloads a file to the given local path and returns the size of the downloaded file if successful
        """
        sec = security or self.security
        total_bytes = 0

        with open(path, 'wb') as f:
            response = await treq.get(self._build_url(security=sec), stream=True)
            async for data_chunk in response.iter_chunks(5 * 1024 ** 2):
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
        response = await treq.get(self._build_url(security=sec))
        return await response.content()

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
        response = await treq.get(obj.signed_url(security=security))
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
        response = await treq.get(obj.signed_url(security=security))
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
        response = await treq.get(obj.signed_url(security=security))
        return await response.json()
```

---

### Key Notes
1. All methods that use `treq` are now asynchronous (`async def`).
2. `await` is used to resolve `treq`'s `Deferred` objects.
3. The `iter_content` method from `requests` is replaced with `response.iter_chunks()` in `treq`.
4. The `response.json()` and `response.content()` methods are awaited to retrieve the response data.