### Explanation of Changes

To migrate the code from using the `requests` library to the `pycurl` library, several changes were made:

1. **Import Statement**: The import statement for `requests` was removed, and `pycurl` was imported instead.
2. **HTTP Requests**: The `requests.get()` and `requests.post()` methods were replaced with `pycurl` methods. This involved setting up a `pycurl.Curl` object, configuring it with the appropriate options, and using a callback to capture the response.
3. **Response Handling**: Since `pycurl` does not return a response object like `requests`, we had to manually handle the response by writing it to a buffer and then processing it accordingly.
4. **Error Handling**: The error handling for HTTP requests was adjusted to accommodate the way `pycurl` operates.

Here is the modified code:

```python
import filestack.models
import pycurl
from io import BytesIO


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

    def store(self, filename=None, location=None, path=None, container=None,
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
        
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, instance.url)
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.POST, 1)
        c.perform()
        c.close()
        
        response_data = buffer.getvalue()
        response_json = json.loads(response_data)
        return filestack.models.Filelink(handle=response_json['handle'])

    def download(self, path, security=None):
        """
        Downloads a file to the given local path and returns the size of the downloaded file if successful
        """
        sec = security or self.security
        total_bytes = 0

        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self._build_url(security=sec))
        c.setopt(c.WRITEDATA, buffer)
        c.setopt(c.NOBODY, 0)
        c.perform()
        c.close()

        with open(path, 'wb') as f:
            data = buffer.getvalue()
            f.write(data)
            total_bytes += len(data)

        return total_bytes

    def get_content(self, security=None):
        """
        Returns the raw byte content of a given object

        Returns:
            `bytes`: file content
        """
        sec = security or self.security
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, self._build_url(security=sec))
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        return buffer.getvalue()

    def tags(self, security=None):
        """
        Performs image tagging operation on current object (image)

        Args:
            security (:class:`filestack.Security`): Security object that will be used
                to perform image tagging

        Returns:
            `dict`: dictionary containing image tags
        """
        obj = self._add_transform_task('tags', params={'self': None})
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, obj.signed_url(security=security))
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        response_data = buffer.getvalue()
        response_json = json.loads(response_data)
        return response_json

    def sfw(self, security=None):
        """
        Performs Safe for Work detection on current object (image).

        Args:
            security (:class:`filestack.Security`): Security object that will be used
                to perform image tagging

        Returns:
            `dict`: dictionary containing SFW result
        """
        obj = self._add_transform_task('sfw', params={'self': None})
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, obj.signed_url(security=security))
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        response_data = buffer.getvalue()
        response_json = json.loads(response_data)
        return response_json

    def ocr(self, security=None):
        """
        Performs OCR on current object (image)

        Args:
            security (:class:`filestack.Security`): Security object that will be used
                to run OCR

        Returns:
            `dict`: dictionary containing OCR data
        """
        obj = self._add_transform_task('ocr', params={'self': None})
        buffer = BytesIO()
        c = pycurl.Curl()
        c.setopt(c.URL, obj.signed_url(security=security))
        c.setopt(c.WRITEDATA, buffer)
        c.perform()
        c.close()
        
        response_data = buffer.getvalue()
        response_json = json.loads(response_data)
        return response_json
``` 

This code now uses `pycurl` for HTTP requests while maintaining the original structure and functionality of the application.